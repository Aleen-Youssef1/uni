import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from scipy.spatial.distance import correlation
import pymysql

# Connect to the MySQL database
db = pymysql.connect(host="localhost", user="root", password="", database="platform1")
cursor = db.cursor()

# Fetch the data from the database
query = "SELECT * FROM user_behavior"
cursor.execute(query)
data = cursor.fetchall()

# Create a pandas DataFrame from the fetched data
df = pd.DataFrame(data, columns=['user_id', 'article_id', 'rating'])

# Create a pivot table for user-item ratings
pivot_table = df.pivot_table(index='user_id', columns='article_id', values='rating')

# Replace missing values with zeros
pivot_table = pivot_table.fillna(0)

# Calculate user-user similarity using Pearson correlation
user_similarity = 1 - pairwise_distances(pivot_table.values, metric="correlation")

# Set user IDs as index and columns
user_similarity_df = pd.DataFrame(user_similarity, index=pivot_table.index, columns=pivot_table.index)
#print("usersim",user_similarity_df)


# Define the number of neighbors to consider
k = 7

# Function to predict ratings for articles not rated by the target user
def predict_rating(user_id, article_id):
    user_ratings = pivot_table.loc[user_id]
    similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:k+1]
    
    weighted_ratings = 0
    total_similarity = 0
    
    for similar_user_id, similarity_score in similar_users.items():
        if pivot_table.loc[similar_user_id, article_id] != 0:
            weighted_ratings += similarity_score * pivot_table.loc[similar_user_id, article_id]
            total_similarity += similarity_score
    
    if total_similarity == 0:
        return 0
    
    predicted_rating = weighted_ratings / total_similarity
    return predicted_rating

# Function to get top N articles predicted to be liked by a user
def get_top_n_articles(user_id, n=7):
    user_articles_rated = pivot_table.columns[pivot_table.loc[user_id] > 0]
    
    unrated_articles = pivot_table.columns[pivot_table.loc[user_id] == 0]
    
    predicted_ratings = []
    for article_id in unrated_articles:
        predicted_rating = predict_rating(user_id, article_id)
        predicted_ratings.append((article_id, predicted_rating))
    
    # Filter out articles the user has already rated
    predicted_ratings = [(article_id, rating) for article_id, rating in predicted_ratings if article_id not in user_articles_rated]
    
    # Sort articles by predicted rating
    predicted_ratings.sort(key=lambda x: x[1], reverse=True)
    
    top_n_articles = predicted_ratings[:n]
    return top_n_articles

# Example: Get top N articles predicted to be liked by a specific user
user_id_to_predict=13
top_n_articles = get_top_n_articles(user_id_to_predict, n=7)

print(f"Top 5 articles predicted to be liked by user {user_id_to_predict}:")
for article_id, predicted_rating in top_n_articles:
    print(f"Article {article_id}, Predicted Rating: {predicted_rating:.2f}")

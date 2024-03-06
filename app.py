import os
import re
import sys
import math
from passlib.hash import bcrypt
from werkzeug.utils import secure_filename
from flask import Flask, redirect, url_for, render_template, request, session
from flask_mysqldb import MySQL
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from scipy.spatial.distance import correlation
import pymysql



app = Flask(__name__)
app.secret_key = '321654987'



def get_user_data():
    if 'userid' in session:
        cur = db.cursor()
        id = session['userid']
        cur.execute('SELECT * FROM user WHERE id=%s', (id,))
        data = cur.fetchone()
        return data
    return None

#start algorithm functions

# Connect to the MySQL database
db = pymysql.connect(host="localhost", user="root", password="", database="platform1")
cursor = db.cursor()
user_ratings = {}  # Dictionary to store user ratings
rated_articles = {}  # Dictionary to store rated articles for each user

# Fetch the data from the database
query = "SELECT * FROM user_behavior"
cursor.execute(query)
data = cursor.fetchall()

# Update user_ratings and rated_articles dictionaries
for row in data:
    user_id = row[0]
    article_id = row[1]
    rating = row[2]
    
    if user_id not in user_ratings:
        user_ratings[user_id] = {}
    
    user_ratings[user_id][article_id] = rating

    if user_id not in rated_articles:
        rated_articles[user_id] = set()
    
    if rating > 0:
        rated_articles[user_id].add(article_id)

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
    if 'userid' in session:
        user_id = session['userid']

        user_articles_rated = rated_articles.get(user_id, set())

        unrated_articles = set(pivot_table.columns) - user_articles_rated

        predicted_ratings = []
        for article_id in unrated_articles:
            predicted_rating = predict_rating(user_id, article_id)
            
            # Only consider articles with predicted rating greater than 2
            if predicted_rating > 2:
                predicted_ratings.append((article_id, predicted_rating))

        # Sort articles by predicted rating
        predicted_ratings.sort(key=lambda x: x[1], reverse=True)

        top_n_articles = predicted_ratings[:n]

        # Move rated articles to the rated_articles dictionary
        rated_articles[user_id] = rated_articles.get(user_id, set()).union(
            [article_id for article_id, _ in top_n_articles]
        )
        for article_id, _ in top_n_articles:
            user_ratings[user_id][article_id] = 0

        return top_n_articles
#end algorithm



@app.route('/')
def home():
    user_data = get_user_data()
    top_n_articles = []  
    cur = db.cursor()
    check_id=[]
    cur.execute('SELECT DISTINCT user_id FROM user_behavior')
    check_id=cur.fetchall()
    result = []
    interest_article=[]
    if 'userid' in session:
        cur.execute('SELECT interests FROM user WHERE id=%s',(session['userid'],))
        data=cur.fetchone()
        cur.execute('SELECT * FROM article WHERE categoryID=%s',(data,))
        interest_article=cur.fetchall()
    if 'userid' in session:
        user_id_to_predict = session['userid']
        
        # Check if the user has rated any articles
        if user_id_to_predict in rated_articles:
            top_n_articles = get_top_n_articles(user_id_to_predict, n=7)
            top_n_article_ids = [article_id for article_id, _ in top_n_articles]
       
            for top_id in top_n_article_ids:
                cur.execute('SELECT * FROM article WHERE id=%s',(top_id,))
                result.extend(cur.fetchall())

    cur.execute('select * from categories')
    categories = cur.fetchall()

    return render_template("home.html", user=user_data, allCategories=categories,  result=result, check_id=check_id,interest_article=interest_article)


@app.route('/categories')
def categories():
     user_data = get_user_data()
     cur = db.cursor()
     cur.execute('select * from categories')
     categories = cur.fetchall()
     return render_template("categories.html",categories=categories,user=user_data)


@app.route('/about')
def about():
    user_data = get_user_data()
    return render_template('about.html', user=user_data)

@app.route('/topics')
def topics():
    user_data = get_user_data()
    return render_template('topics.html', user=user_data)

@app.route('/contact')
def contact():
    user_data = get_user_data()
    return render_template('contact.html', user=user_data)

@app.route('/profile')
def profile():
    user_data = get_user_data()
    cr = db.cursor()
    
    cr.execute('SELECT COUNT(rating) AS rated_articles FROM user_behavior WHERE user_id =%s;' , (user_data[0],))
    countArticle = cr.fetchall()[0][0]
   
    return render_template('profile.html',user=user_data,countArticle=countArticle)


@app.route('/admain_profile')
def admain_profile():
   user_data = get_user_data()
   cr=db.cursor()
   #manage_info=[]
   cr.execute('SELECT COUNT(ID) FROM user')
   manage_info=cr.fetchall()[0][0]
   cr.execute('SELECT COUNT(id)FROM article')
   articlesInfo=cr.fetchall()[0][0]
   
   cr.execute('select * from categories')
   categories = cr.fetchall()
   return render_template('admain_profile.html',user=user_data,manage_info=manage_info,allCategories=categories,articlesInfo=articlesInfo)


def upload_image(image_file):
    upload_folder = 'static\images'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    image_path = os.path.join(upload_folder, image_file.filename)
    image_file.save(image_path)
    return image_path

# Registration form
@app.route('/register', methods=['GET', 'POST'])
def register():
    user_data = get_user_data()
    message = ''
    categories = []
    cr = db.cursor()
    cr.execute('SELECT * FROM categories')
    categories = cr.fetchall()

    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'pass' in request.form:
        userName = request.form['name']
        email = request.form['email']
        password = request.form['pass']
        Cpassword = request.form['c_pass']
        age = request.form['age']
        interest = request.form['interest']
        image = request.files['image']

        cr.execute('SELECT * FROM user WHERE email=%s', (email,))
        account = cr.fetchall()
        if account:
            message = 'Already exist!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email!!'
        elif not userName or not password or not email:
            message = 'Fill out all fields'
        elif Cpassword!= password:
            message = 'Confirm password correctly'
       
        else:
            image_path = upload_image(image)
            hashed_password = bcrypt.hash(password)
            cr.execute('INSERT INTO user (name, email, pass, age, interests, imagePath) VALUES (%s, %s, %s, %s, %s, %s)', (userName, email, hashed_password, age, interest,image_path))
            
            message = 'Successful'
            return render_template('login.html', message=message,user=user_data)
    return render_template('register.html', categories=categories, message=message,user=user_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    user_data = get_user_data()
    cursor = db.cursor()
   
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'pass' in request.form:
        email = request.form['email']
        password =request.form['pass']
        cursor.execute('SELECT * FROM user WHERE email=%s', (email,))
        user = cursor.fetchone()
        if  user:
            if 'userid' in session :
                message = 'you logged in as '+str(session['name'])
                return redirect(url_for('home', message=message))
            else:
                if user and bcrypt.verify(password, user[4]):
                    session['loggedin'] = True
                    session['userid'] = user[0]  
                    session['name'] = user[2]  
                    session['email'] = user[3]  
                    session['image'] = user[7]  


                    message = 'Success login'
                    return redirect(url_for('home', message=message))
                else:
                    message = 'Please enter valid input'
                    return redirect(url_for('login', message=message))
        else:
            message='you dont have an acount, Sign up please'
            return redirect(url_for('register', message=message))
    return render_template('login.html', message=message, user=user_data)
   
@app.route('/logout')
def logout():
    session.clear()
    
    return redirect(url_for('home'))

@app.route('/articles/<int:id>')
def articles(id):
    user_data = get_user_data()
    cr = db.cursor()
    cr.execute('select * from article where categoryID =%s', (id,))
    articles=cr.fetchall()
    return render_template('articles.html',user=user_data, articles=articles)


    

@app.route('/show_article/<int:id>', methods=['POST', 'GET'])
def show_article(id):

    user_data = get_user_data()
    cr = db.cursor()
    cr.execute('SELECT * FROM article WHERE id = %s', (id,))
    article = cr.fetchone()

    if request.method == 'POST':
        rating = request.form['rating']
        user_id = request.form['user_id']

        # Check if the user has already rated the article
        cr.execute('SELECT * FROM user_behavior WHERE user_id = %s AND article_id = %s', (user_id, id))
        existing_rating = cr.fetchone()

        if existing_rating:
            # Update the existing rating
            cr.execute('UPDATE user_behavior SET rating = %s WHERE user_id = %s AND article_id = %s', (rating, user_id, id))
        else:
            # Insert a new rating
            cr.execute('INSERT INTO user_behavior (user_id, article_id, rating) VALUES (%s, %s, %s)', (user_id, id, rating))

        cr.close()

    return render_template('show_article.html', user=user_data, article=article)


@app.route('/add_category', methods=['POST', 'GET'])
def add_category():
    user_data = get_user_data()
    message = ''
    cr = db.cursor()
    

    if request.method == 'POST' and 'title' in request.form and 'description' in request.form and 'img' in request.files:
        title = request.form['title']
        description = request.form['description']
        image = request.files['img']  

        cr.execute('SELECT * FROM article WHERE title=%s', (title,))
        categ = cr.fetchall()
        if categ:
            message = 'The article already exists'
        else:
            image_path = upload_image(image)

            
            cr.execute('INSERT INTO categories (title, description, imgpath) VALUES (%s, %s, %s)', (title, description, image_path ))
            
            return redirect(url_for('home',user=user_data))

    return render_template('add_category.html', message=message,user=user_data)


@app.route('/add_article', methods=['POST', 'GET'])
def add_article():
    message = ''
    user_data = get_user_data()
    categories = []
    cr = db.cursor()
    cr.execute('SELECT * FROM categories')
    categories = cr.fetchall()

    if request.method == 'POST' and 'addart' in request.form and 'interest' in request.form and 'image' in request.files:
        title = request.form['title']
        addart = request.form['addart']
        interest = request.form['interest']
        image = request.files['image']

        # Store the article in the 
        image_path=upload_image(image)
        cr.execute('INSERT INTO article (title, artc_text, img_path, categoryID) VALUES (%s, %s, %s, %s)', (title, addart, image_path, interest))
       

        
        
        message = 'Article added successfully'

    return render_template('add_article.html', message=message, categories=categories,user=user_data)


@app.route('/update_user',methods=['POST', 'GET'])
def update_user():
    user_data = get_user_data()
    cr = db.cursor()
    if request.method == 'POST':
        
        if 'save_profile' in request.form:
          
            name = request.form.get('name')
            email = request.form.get('email')
            image = request.files['image']
            if image:
             imagePath=upload_image(image)
             cr.execute('UPDATE user SET name=%s, email=%s, imagePath=%s WHERE id=%s',(name,email,imagePath,user_data[0]))
             return "Profile updated successfully!"
            else:
             cr.execute('UPDATE user SET name=%s, email=%s WHERE id=%s', (name, email, user_data[0]))

            
             return "Profile updated successfully!"
        
        elif 'save_password' in request.form:
            # Update password
            old_password = request.form.get('old_pass')
            new_password = request.form.get('new_pass')
            confirm_password = request.form.get('c_pass')
            password= bcrypt.hash(new_password)

            if bcrypt.verify(old_password, user_data[4]) and new_password == confirm_password:
             cr.execute('UPDATE user SET pass=%s WHERE id=%s',( password,user_data[0]))
           
            return "update succesful"
            
        else:
            return "password or confim not correct"
           
    return render_template('update_user.html',user=user_data)


@app.route('/user')
def user():
    user_data = get_user_data()
    cr = db.cursor()
    cr.execute('select * from user where id!=%s',(user_id,))
    users_info=cr.fetchall()
    cur=db.cursor()
    cur.execute('SELECT  user_id FROM user_behavior;')
    user_ids=[]
    user_ids=cur.fetchall()
    
    for id in user_ids:
            cur.execute('SELECT user_id, AVG(rating)FROM user_behavior WHERE user_id=%s',(id,))
            average_rate=cur.fetchall()
        
    return render_template('user.html',user=user_data, users_info= users_info,average_rate=average_rate)


@app.route('/view_articles')
def view_articles():
     user_data = get_user_data()
     cr = db.cursor()
     cr.execute('select * from article ')
     article_info=cr.fetchall()
     return render_template('view_articles.html',article_info=article_info,user=user_data)

def get_article_data(article_id):
    cr = db.cursor()
    query = "SELECT * FROM article WHERE id = %s"
    cr.execute(query, (article_id,))
    return cr.fetchone()

@app.route('/update_article/<int:id>', methods=['GET', 'POST'])
def update_article(id):
    user_data = get_user_data() 
    article_data = get_article_data(id)
    message = ''
    categories = []
    cr = db.cursor()
    cr.execute('SELECT * FROM categories')
    categories = cr.fetchall()

    if request.method == 'POST':
        article_title = request.form['title']
        article_content = request.form['addart']
        category = request.form['interest']
        image = request.files['image']
        message='updated successfuly'
        
        image_path =upload_image(image)
        cr.execute('UPDATE article SET title=%s, artc_text=%s, img_path=%s, categoryID=%s WHERE id=%s', (article_title, article_content, image_path, category, id))

        
   
    return render_template('update_article.html', user=user_data, article=article_data, categories=categories , message= message)


@app.route('/delete_article/<int:id>')
def delete_article(id):
    cr = db.cursor()
    # Delete from article table
    cr.execute('DELETE FROM article WHERE id = %s', (id,))

    # Delete from user_behavior table
    cr.execute('DELETE FROM user_behavior WHERE article_id = %s', (id,))


    return redirect(url_for('view_articles'))  # Redirect to a page where articles are listed

@app.route('/update_category/<int:id>', methods=['GET', 'POST'])
def update_category(id):
     message=''
     user_data = get_user_data()
     cr = db.cursor()
     cr.execute('SELECT * FROM categories WHERE id=%s',(id,))
     categories = cr.fetchone()
     if request.method == 'POST':
        category_title=request.form['title']
        description=request.form['description']
        image=request.files['img']
        image_path =upload_image(image)
        cr.execute('UPDATE categories SET title=%s, description=%s, imgpath=%s WHERE id=%s',(category_title,description,image_path,id) )
        message='updated successfulys'
     return render_template('update_category.html', user=user_data, categories=categories , message= message)






if __name__ == '__main__':
    app.secret_key = '321654987'
    app.run(debug=True)
-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jun 25, 2023 at 08:08 PM
-- Server version: 5.7.36
-- PHP Version: 7.4.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `platform1`
--

-- --------------------------------------------------------

--
-- Table structure for table `article`
--

DROP TABLE IF EXISTS `article`;
CREATE TABLE IF NOT EXISTS `article` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) CHARACTER SET utf8 NOT NULL,
  `artc_text` text CHARACTER SET utf8 NOT NULL,
  `img_path` varchar(100) CHARACTER SET utf8 NOT NULL,
  `categoryID` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `courseID` (`categoryID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
CREATE TABLE IF NOT EXISTS `categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(50) NOT NULL,
  `description` varchar(200) NOT NULL,
  `imgpath` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `categories`
--

INSERT INTO `categories` (`id`, `title`, `description`, `imgpath`) VALUES
(1, 'python', ' <select name=\"inputorigin\" required class=\"box\"> <select name=\"inputorigin\" required class=\"box\">', ''),
(2, 'html', ' <select name=\"inputorigin\" required class=\"box\">', '');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `authority` tinyint(1) NOT NULL DEFAULT '0',
  `name` varchar(50) CHARACTER SET utf8 NOT NULL,
  `email` varchar(100) CHARACTER SET utf8 NOT NULL,
  `password` varchar(100) CHARACTER SET utf8 NOT NULL,
  `age` int(11) NOT NULL,
  `interests` varchar(100) CHARACTER SET utf8 NOT NULL,
  `imagePath` varchar(100) NOT NULL,
  `reg_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `email` (`email`)
) ENGINE=MyISAM AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `authority`, `name`, `email`, `password`, `age`, `interests`, `imagePath`, `reg_time`) VALUES
(1, 0, 'asaa', 'adsdsads@gmail.com', '123', 25, '2', '<FileStorage: \'188341147_4643136819052684_8164208564098678622_n.jpg\' (\'image/jpeg\')>', '2023-05-26 17:00:27'),
(2, 0, 'fdsfsdf', 'rhrhrhnfghf@gmail.com', '123', 25, '2', '<FileStorage: \'188341147_4643136819052684_8164208564098678622_n.jpg\' (\'image/jpeg\')>', '2023-05-26 17:00:54'),
(3, 1, 'Aleen', 'asdfgh@gmail.com', '321', 19, '2', '<FileStorage: \'[Downloader.la]-634098a2f085b.jpg\' (\'image/jpeg\')>', '2023-05-27 09:48:50'),
(4, 0, 'asd', 'adsfg@gmail.com', '123', 22, '2', '<FileStorage: \'[Downloader.la]-6340981976852.jpg\' (\'image/jpeg\')>', '2023-05-27 09:52:30'),
(5, 0, 'fiujk', 'dfgheorgho@gmail.com', '123', 100, '1', '<FileStorage: \'[Downloader.la]-63409544f3591.jpg\' (\'image/jpeg\')>', '2023-05-27 09:56:54'),
(6, 0, 'sfdwffe', 'fefergrtgrt@gmail.com', '123', 55, '1', '<FileStorage: \'[Downloader.la]-634096f9c8327.jpg\' (\'image/jpeg\')>', '2023-05-27 10:02:40'),
(7, 0, 'dscds', 'fgfhgrjty@gmail.com', '123', 15, '1', '<FileStorage: \'[Downloader.la]-634096c225905.jpg\' (\'image/jpeg\')>', '2023-05-27 13:43:43'),
(8, 0, 'dede', 'asddgdf@gmail.com', '$2b$12$XLxzmYXOZPd2E7VEm2yC7.KogPaTyZu.f8m70HzBs4KUZnLlVRZSe', 20, '1', '<FileStorage: \'198969122_497863271495587_4098333381411781342_n.png\' (\'image/png\')>', '2023-06-23 13:09:50'),
(9, 0, 'sadas', 'sdfds@gmail.com', '$2b$12$aFm9ATRswCUQ1yeZ9.WC.uk3SVRB0ArYLJCsVITYFcGMe7C1Nt6mS', 31, '2', '<FileStorage: \'[GetPaidStock.com]-63558ab40da77.jpg\' (\'image/jpeg\')>', '2023-06-25 07:45:14'),
(10, 0, 'aleeenova', 'asd@gmail.com', '$2b$12$vkkvI.FXws2FSZUnK0e1Y.q4CzemUSIyHwg22/nsBDyEh60lnuT8q', 50, '2', '<FileStorage: \'[GetPaidStock.com]-63558a76dab46.jpg\' (\'image/jpeg\')>', '2023-06-25 14:54:11');

-- --------------------------------------------------------

--
-- Table structure for table `user_behavior`
--

DROP TABLE IF EXISTS `user_behavior`;
CREATE TABLE IF NOT EXISTS `user_behavior` (
  `user_id` int(11) NOT NULL,
  `article_id` int(11) NOT NULL,
  `rating` float NOT NULL,
  PRIMARY KEY (`user_id`,`article_id`),
  KEY `article_id` (`article_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

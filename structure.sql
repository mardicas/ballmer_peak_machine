-- phpMyAdmin SQL Dump
-- version 4.2.12deb2+deb8u2
-- http://www.phpmyadmin.net
--
-- Host: mysql
-- Generation Time: May 03, 2019 at 07:13 AM
-- Server version: 5.5.62-0+deb8u1
-- PHP Version: 5.6.24-0+deb8u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `identity`
--
CREATE DATABASE IF NOT EXISTS `identity` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;

GRANT ALL PRIVILEGES ON `identity`.* TO 'identity'@'%';

GRANT USAGE ON *.* TO 'identity_ro'@'%' IDENTIFIED BY PASSWORD 'ChangeMeToo';
GRANT SELECT ON `identity`.* TO 'identity_ro'@'%';


USE `identity`;

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE IF NOT EXISTS `orders` (
`id` int(11) NOT NULL,
  `aeg` datetime NOT NULL,
  `rfid` varchar(16) NOT NULL,
  `slot` varchar(11) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE IF NOT EXISTS `users` (
  `rfid` varchar(16) CHARACTER SET utf8 NOT NULL,
  `name` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `lastscan` datetime NOT NULL,
  `credit` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`  ADD PRIMARY KEY (`id`), ADD UNIQUE KEY `aeg_idx` (`aeg`), ADD KEY `rfid_idx` (`rfid`), ADD KEY `slot_idx` (`slot`);

--
-- Indexes for table `users`
--
ALTER TABLE `users` ADD PRIMARY KEY (`rfid`), ADD KEY `name` (`name`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders` MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=1;

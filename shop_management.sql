-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 10, 2026 at 07:15 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `shop_management`
--

-- --------------------------------------------------------

--
-- Table structure for table `posts`
--

CREATE TABLE `posts` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  `discount` decimal(5,2) DEFAULT NULL,
  `offer_counter` int(11) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `admin_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `posts`
--

INSERT INTO `posts` (`id`, `title`, `description`, `image_path`, `discount`, `offer_counter`, `created_at`, `admin_id`) VALUES
(3, 'Utran Special', 'Greet Discount 30%', '20251127_124940_download.jpg', 30.00, 0, '2025-11-27 07:19:40', 1);

-- --------------------------------------------------------

--
-- Table structure for table `premium_cards`
--

CREATE TABLE `premium_cards` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `card_number` varchar(12) NOT NULL,
  `qr_code_path` varchar(255) DEFAULT NULL,
  `visits` int(11) DEFAULT 0,
  `total_discount` decimal(10,2) DEFAULT 0.00,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `pdf_path` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `premium_cards`
--

INSERT INTO `premium_cards` (`id`, `user_id`, `card_number`, `qr_code_path`, `visits`, `total_discount`, `created_at`, `pdf_path`) VALUES
(54, 17, '055412892347', 'qr_055412892347.png', 3, 1540.00, '2025-11-27 13:58:18', 'card_055412892347.png'),
(110, 19, '987240713735', 'qr_987240713735.png', 1, 1500.00, '2025-11-28 07:58:15', 'card_987240713735.png'),
(162, 16, '179250628071', 'qr_179250628071.png', 2, 850.00, '2025-12-23 03:46:43', 'card_179250628071.png'),
(164, 20, '838138185085', 'qr_838138185085.png', 1, 500.00, '2025-12-31 07:57:24', 'card_838138185085.png'),
(165, 21, '564880223551', 'qr_564880223551.png', 1, 75.00, '2025-12-31 08:14:46', 'card_564880223551.png');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password` varchar(255) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `is_admin` tinyint(1) DEFAULT 0,
  `email_verified` tinyint(1) DEFAULT 0,
  `verification_token` varchar(100) DEFAULT NULL,
  `reset_token` varchar(100) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `email`, `password`, `name`, `address`, `phone`, `is_admin`, `email_verified`, `verification_token`, `reset_token`, `created_at`) VALUES
(1, 'patniashish28@gmail.com', 'scrypt:32768:8:1$xttlAF6R4pCuMsAw$eb2840f702fbc81e68f726160bb0ec0cc8460e45c5b10092d829672b98ac20b9b97ceb78d577d74eccaa50427c51bdc65ca748424d3995d5255968f8712c41e4', 'Admin', NULL, NULL, 1, 1, NULL, NULL, '2025-11-26 08:00:19'),
(16, 'patniakash304@gmail.com', 'scrypt:32768:8:1$WuF1VNRyxqvpRVmp$aeafba828cb233991221993b9e1901c6467971707fcbf3bcba604de85e49db13167e5ca48898b89266e74ada459c06d3004a0fe5558786a3d35c8df37f97f407', 'Akash Patni', '4,bholeshankar society, chandulal ni chali, near vikram mill compound bapunagar, ahmedabad', '9624504501', 0, 1, NULL, NULL, '2025-11-27 13:50:23'),
(17, 'aniketpatani8@gmail.com', 'scrypt:32768:8:1$3AIRxAxe9G1DXk2f$b9757d72ddfd678837a62042d89217fee9d1bd8bcaf4215fce72ca7d2581ec158d1db6ea334f9e5e6f7e0b8bb13da0113cab86a73d6d02717d0f54169462bd7f', 'Aniket', 'Bapunagar', '9328403672', 0, 1, NULL, NULL, '2025-11-27 14:00:18'),
(19, 'abc123@gmail.com', 'scrypt:32768:8:1$JjjzWPrTtheY9oFC$bdec2de216e0d08f0dd90fafe19f1813f0ec44854fa0432ae150ed692b25ac4fcd20a5a0894a024ad4ad27b6d5f3fa83ff7fce06ceba80fab767bc3b8052e36d', 'Nilesh patni', '4 bholeshankar ', '9624504501', 0, 1, NULL, NULL, '2025-11-28 07:59:41'),
(20, 'bpraja440@gmail.com', 'scrypt:32768:8:1$xiYln1gJtGHcJk4J$09d88fc7262ce81378c02dba9068f2952595317f3063c8711efe57a3cf76073c1cabcede2afb737c27e17e2e22d14c29dd231f0b17e35b067833a8e431058399', 'Bhupa Bhai', 'Motisah,Patan', '7623802464', 0, 1, NULL, NULL, '2025-12-31 08:00:48'),
(21, 'patnivikrambhai@gmail.com', 'scrypt:32768:8:1$zG8PJ3gwB62Oz385$9e62879078942b9a89920b735855ef6d69004793b35ab4ea4d746be47c6afa13fc7034a8a7c7f87642259c21652abc7f54d1bd176e4c2d1ef9e21de112216edf', 'Vikrambhai', 'Saraspur,Ahmedabad ', '8849275540', 0, 1, NULL, NULL, '2025-12-31 08:18:42'),
(22, 'mahendarnaran@gmail.com', 'scrypt:32768:8:1$df9rM0wwkQxsdcN4$9ee408e0e588b171b1005f31dfae0c45cf02d623b800554f1ce6f1c1ef2d3573bf6c8b618e345fb52bf571db97f8d3c84d26aa66be23b1ed2e56c95735706a56', 'Admin', NULL, NULL, 1, 1, NULL, NULL, '2025-12-31 09:03:47');

-- --------------------------------------------------------

--
-- Table structure for table `visits`
--

CREATE TABLE `visits` (
  `id` int(11) NOT NULL,
  `card_id` int(11) DEFAULT NULL,
  `product_info` text DEFAULT NULL,
  `purchase_amount` decimal(10,2) DEFAULT 0.00,
  `discount_applied` decimal(10,2) DEFAULT NULL,
  `visit_date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `visits`
--

INSERT INTO `visits` (`id`, `card_id`, `product_info`, `purchase_amount`, `discount_applied`, `visit_date`) VALUES
(5, 54, 'dori', 0.00, 20.00, '2025-11-27 14:07:17'),
(6, 54, 'dori', 5000.00, 1500.00, '2025-11-27 14:15:04'),
(7, 110, 'Fatakda', 10000.00, 1500.00, '2025-11-28 08:00:53'),
(8, 162, 'દોરી પતંગ ', 5000.00, 500.00, '2025-12-23 04:13:10'),
(9, 162, 'ચાયના દોરી ', 3500.00, 350.00, '2025-12-23 04:18:58'),
(10, 164, 'Patang-dori', 5000.00, 500.00, '2025-12-31 08:04:45'),
(11, 165, 'Fireworks ', 500.00, 75.00, '2025-12-31 08:22:06');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `posts`
--
ALTER TABLE `posts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `admin_id` (`admin_id`);

--
-- Indexes for table `premium_cards`
--
ALTER TABLE `premium_cards`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `card_number` (`card_number`),
  ADD KEY `premium_cards_ibfk_1` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `visits`
--
ALTER TABLE `visits`
  ADD PRIMARY KEY (`id`),
  ADD KEY `card_id` (`card_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `posts`
--
ALTER TABLE `posts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `premium_cards`
--
ALTER TABLE `premium_cards`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=166;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `visits`
--
ALTER TABLE `visits`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `posts`
--
ALTER TABLE `posts`
  ADD CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `premium_cards`
--
ALTER TABLE `premium_cards`
  ADD CONSTRAINT `premium_cards_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `visits`
--
ALTER TABLE `visits`
  ADD CONSTRAINT `visits_ibfk_1` FOREIGN KEY (`card_id`) REFERENCES `premium_cards` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

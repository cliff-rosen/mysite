-- --------------------------------------------------------
-- Host:                         database-1.cc98c9tzk3rq.us-east-2.rds.amazonaws.com
-- Server version:               10.6.10-MariaDB-log - managed by https://aws.amazon.com/rds/
-- Server OS:                    Linux
-- HeidiSQL Version:             11.0.0.5919
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Dumping database structure for doc
CREATE DATABASE IF NOT EXISTS `doc` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `doc`;

-- Dumping structure for table doc.conversation
CREATE TABLE IF NOT EXISTS `conversation` (
  `conversation_id` varchar(20) NOT NULL DEFAULT '',
  `user_id` int(11) NOT NULL DEFAULT 0,
  `domain_id` int(11) NOT NULL DEFAULT 0,
  `conversation_text` text NOT NULL DEFAULT '0',
  `date_time_started` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  KEY `Index 1` (`conversation_id`),
  KEY `FK__user` (`user_id`),
  KEY `FK__domain` (`domain_id`),
  CONSTRAINT `FK__domain` FOREIGN KEY (`domain_id`) REFERENCES `domain` (`domain_id`),
  CONSTRAINT `FK__user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table doc.document
CREATE TABLE IF NOT EXISTS `document` (
  `doc_id` int(11) NOT NULL AUTO_INCREMENT,
  `domain_id` int(11) NOT NULL,
  `doc_uri` varchar(500) NOT NULL,
  `doc_title` text DEFAULT '0',
  `doc_text` longtext NOT NULL,
  PRIMARY KEY (`doc_id`),
  KEY `FK_document_domain` (`domain_id`),
  CONSTRAINT `FK_document_domain` FOREIGN KEY (`domain_id`) REFERENCES `domain` (`domain_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21196 DEFAULT CHARSET=utf8mb4;

-- Data exporting was unselected.

-- Dumping structure for table doc.document_chunk
CREATE TABLE IF NOT EXISTS `document_chunk` (
  `doc_chunk_id` int(11) NOT NULL AUTO_INCREMENT,
  `doc_id` int(11) NOT NULL,
  `chunk_text` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_nopad_ci NOT NULL DEFAULT '',
  `chunk_embedding` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT '',
  PRIMARY KEY (`doc_chunk_id`)
) ENGINE=InnoDB AUTO_INCREMENT=45161 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table doc.doc_temp
CREATE TABLE IF NOT EXISTS `doc_temp` (
  `doc_id` int(11) NOT NULL AUTO_INCREMENT,
  `domain_id` int(11) DEFAULT NULL,
  `doc_uri` varchar(500) CHARACTER SET utf8mb4 DEFAULT NULL,
  `doc_title` text CHARACTER SET utf8mb4 DEFAULT '0',
  `doc_text` longtext CHARACTER SET utf8mb4 NOT NULL,
  PRIMARY KEY (`doc_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table doc.domain
CREATE TABLE IF NOT EXISTS `domain` (
  `domain_id` int(11) NOT NULL AUTO_INCREMENT,
  `domain_desc` varchar(50) DEFAULT '0',
  `spider_notes` text DEFAULT NULL,
  KEY `Index 1` (`domain_id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table doc.query_log
CREATE TABLE IF NOT EXISTS `query_log` (
  `query_id` int(11) NOT NULL AUTO_INCREMENT,
  `query_text` text NOT NULL,
  `query_prompt` text NOT NULL,
  `query_temp` float NOT NULL,
  `query_timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `domain_id` int(11) DEFAULT NULL,
  `response_text` text NOT NULL,
  `response_chunk_ids` varchar(100) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  KEY `Index 1` (`query_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1188 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table doc.user
CREATE TABLE IF NOT EXISTS `user` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_name` varchar(16) NOT NULL,
  `user_description` varchar(200) DEFAULT NULL,
  `password` varchar(100) NOT NULL,
  `date_time_created` timestamp NOT NULL DEFAULT current_timestamp(),
  `domain_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE KEY `UserName` (`user_name`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;

-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               10.3.23-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             11.0.0.5919
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;

-- Dumping structure for table doc.document
CREATE TABLE IF NOT EXISTS `document` (
  `doc_id` int(11) NOT NULL AUTO_INCREMENT,
  `domain_id` int(11) NOT NULL,
  `doc_uri` varchar(250) NOT NULL DEFAULT '0',
  `doc_title` tinytext DEFAULT '0',
  `doc_text` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_nopad_ci NOT NULL,
  PRIMARY KEY (`doc_id`),
  KEY `FK_document_domain` (`domain_id`),
  CONSTRAINT `FK_document_domain` FOREIGN KEY (`domain_id`) REFERENCES `domain` (`domain_id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=latin1;

-- Dumping data for table doc.document: ~0 rows (approximately)
/*!40000 ALTER TABLE `document` DISABLE KEYS */;
/*!40000 ALTER TABLE `document` ENABLE KEYS */;

-- Dumping structure for table doc.document_chunk
CREATE TABLE IF NOT EXISTS `document_chunk` (
  `doc_chunk_id` int(11) NOT NULL AUTO_INCREMENT,
  `doc_id` int(11) NOT NULL,
  `chunk_text` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_nopad_ci NOT NULL DEFAULT '',
  `chunk_embedding` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT '',
  PRIMARY KEY (`doc_chunk_id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=latin1;

-- Dumping data for table doc.document_chunk: ~17 rows (approximately)
/*!40000 ALTER TABLE `document_chunk` DISABLE KEYS */;
/*!40000 ALTER TABLE `document_chunk` ENABLE KEYS */;

-- Dumping structure for table doc.domain
CREATE TABLE IF NOT EXISTS `domain` (
  `domain_id` int(11) NOT NULL AUTO_INCREMENT,
  `domai_desc` varchar(50) DEFAULT '0',
  KEY `Index 1` (`domain_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Dumping data for table doc.domain: ~0 rows (approximately)
/*!40000 ALTER TABLE `domain` DISABLE KEYS */;
/*!40000 ALTER TABLE `domain` ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;

-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: nexus
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add aluno',7,'add_aluno'),(26,'Can change aluno',7,'change_aluno'),(27,'Can delete aluno',7,'delete_aluno'),(28,'Can view aluno',7,'view_aluno'),(29,'Can add curso',8,'add_curso'),(30,'Can change curso',8,'change_curso'),(31,'Can delete curso',8,'delete_curso'),(32,'Can view curso',8,'view_curso'),(33,'Can add professor',9,'add_professor'),(34,'Can change professor',9,'change_professor'),(35,'Can delete professor',9,'delete_professor'),(36,'Can view professor',9,'view_professor'),(37,'Can add disciplina',10,'add_disciplina'),(38,'Can change disciplina',10,'change_disciplina'),(39,'Can delete disciplina',10,'delete_disciplina'),(40,'Can view disciplina',10,'view_disciplina'),(41,'Can add matricula',11,'add_matricula'),(42,'Can change matricula',11,'change_matricula'),(43,'Can delete matricula',11,'delete_matricula'),(44,'Can view matricula',11,'view_matricula'),(45,'Can add frequencia',12,'add_frequencia'),(46,'Can change frequencia',12,'change_frequencia'),(47,'Can delete frequencia',12,'delete_frequencia'),(48,'Can view frequencia',12,'view_frequencia'),(49,'Can add nota',13,'add_nota'),(50,'Can change nota',13,'change_nota'),(51,'Can delete nota',13,'delete_nota'),(52,'Can view nota',13,'view_nota'),(53,'Can add turma',14,'add_turma'),(54,'Can change turma',14,'change_turma'),(55,'Can delete turma',14,'delete_turma'),(56,'Can view turma',14,'view_turma');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(7,'escola','aluno'),(8,'escola','curso'),(10,'escola','disciplina'),(12,'escola','frequencia'),(11,'escola','matricula'),(13,'escola','nota'),(9,'escola','professor'),(14,'escola','turma'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-11-22 12:29:18.442175'),(2,'auth','0001_initial','2025-11-22 12:29:27.695697'),(3,'admin','0001_initial','2025-11-22 12:29:28.671083'),(4,'admin','0002_logentry_remove_auto_add','2025-11-22 12:29:28.769054'),(5,'admin','0003_logentry_add_action_flag_choices','2025-11-22 12:29:28.877363'),(6,'contenttypes','0002_remove_content_type_name','2025-11-22 12:29:29.576244'),(7,'auth','0002_alter_permission_name_max_length','2025-11-22 12:29:29.998764'),(8,'auth','0003_alter_user_email_max_length','2025-11-22 12:29:30.310360'),(9,'auth','0004_alter_user_username_opts','2025-11-22 12:29:30.360111'),(10,'auth','0005_alter_user_last_login_null','2025-11-22 12:29:30.681223'),(11,'auth','0006_require_contenttypes_0002','2025-11-22 12:29:30.688685'),(12,'auth','0007_alter_validators_add_error_messages','2025-11-22 12:29:30.777118'),(13,'auth','0008_alter_user_username_max_length','2025-11-22 12:29:31.290225'),(14,'auth','0009_alter_user_last_name_max_length','2025-11-22 12:29:33.621788'),(15,'auth','0010_alter_group_name_max_length','2025-11-22 12:29:33.873122'),(16,'auth','0011_update_proxy_permissions','2025-11-22 12:29:33.951213'),(17,'auth','0012_alter_user_first_name_max_length','2025-11-22 12:29:34.230804'),(18,'escola','0001_initial','2025-11-22 12:29:38.552000'),(19,'sessions','0001_initial','2025-11-22 12:29:38.781119');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `escola_aluno`
--

DROP TABLE IF EXISTS `escola_aluno`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `escola_aluno` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `matricula` varchar(20) NOT NULL,
  `nome` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `cpf` varchar(14) NOT NULL,
  `data_nascimento` date NOT NULL,
  `telefone` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `matricula` (`matricula`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `cpf` (`cpf`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `escola_aluno`
--

LOCK TABLES `escola_aluno` WRITE;
/*!40000 ALTER TABLE `escola_aluno` DISABLE KEYS */;
/*!40000 ALTER TABLE `escola_aluno` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `escola_curso`
--

DROP TABLE IF EXISTS `escola_curso`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `escola_curso` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `codigo` varchar(20) NOT NULL,
  `descricao` longtext,
  `carga_horaria` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `escola_curso`
--

LOCK TABLES `escola_curso` WRITE;
/*!40000 ALTER TABLE `escola_curso` DISABLE KEYS */;
/*!40000 ALTER TABLE `escola_curso` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `escola_disciplina`
--

DROP TABLE IF EXISTS `escola_disciplina`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `escola_disciplina` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `ementa` longtext,
  `curso_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `escola_disciplina_curso_id_97737521_fk_escola_curso_id` (`curso_id`),
  CONSTRAINT `escola_disciplina_curso_id_97737521_fk_escola_curso_id` FOREIGN KEY (`curso_id`) REFERENCES `escola_curso` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `escola_disciplina`
--

LOCK TABLES `escola_disciplina` WRITE;
/*!40000 ALTER TABLE `escola_disciplina` DISABLE KEYS */;
/*!40000 ALTER TABLE `escola_disciplina` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `escola_frequencia`
--

DROP TABLE IF EXISTS `escola_frequencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `escola_frequencia` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `data_aula` date NOT NULL,
  `presente` tinyint(1) NOT NULL,
  `justificativa` longtext,
  `disciplina_id` bigint NOT NULL,
  `matricula_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `escola_frequencia_disciplina_id_fed01dbd_fk_escola_disciplina_id` (`disciplina_id`),
  KEY `escola_frequencia_matricula_id_f2b50319_fk_escola_matricula_id` (`matricula_id`),
  CONSTRAINT `escola_frequencia_disciplina_id_fed01dbd_fk_escola_disciplina_id` FOREIGN KEY (`disciplina_id`) REFERENCES `escola_disciplina` (`id`),
  CONSTRAINT `escola_frequencia_matricula_id_f2b50319_fk_escola_matricula_id` FOREIGN KEY (`matricula_id`) REFERENCES `escola_matricula` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `escola_frequencia`
--

LOCK TABLES `escola_frequencia` WRITE;
/*!40000 ALTER TABLE `escola_frequencia` DISABLE KEYS */;
/*!40000 ALTER TABLE `escola_frequencia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `escola_matricula`
--

DROP TABLE IF EXISTS `escola_matricula`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `escola_matricula` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `data_matricula` date NOT NULL,
  `status` varchar(20) NOT NULL,
  `aluno_id` bigint NOT NULL,
  `turma_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `escola_matricula_turma_id_ee3074aa_fk_escola_turma_id` (`turma_id`),
  KEY `escola_matricula_aluno_id_522b62c6_fk_escola_aluno_id` (`aluno_id`),
  CONSTRAINT `escola_matricula_aluno_id_522b62c6_fk_escola_aluno_id` FOREIGN KEY (`aluno_id`) REFERENCES `escola_aluno` (`id`),
  CONSTRAINT `escola_matricula_turma_id_ee3074aa_fk_escola_turma_id` FOREIGN KEY (`turma_id`) REFERENCES `escola_turma` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `escola_matricula`
--

LOCK TABLES `escola_matricula` WRITE;
/*!40000 ALTER TABLE `escola_matricula` DISABLE KEYS */;
/*!40000 ALTER TABLE `escola_matricula` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `escola_nota`
--

DROP TABLE IF EXISTS `escola_nota`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `escola_nota` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `valor` decimal(5,2) NOT NULL,
  `tipo_avaliacao` varchar(50) NOT NULL,
  `data_lancamento` date NOT NULL,
  `disciplina_id` bigint NOT NULL,
  `matricula_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `escola_nota_disciplina_id_0938685c_fk_escola_disciplina_id` (`disciplina_id`),
  KEY `escola_nota_matricula_id_cbae3eaa_fk_escola_matricula_id` (`matricula_id`),
  CONSTRAINT `escola_nota_disciplina_id_0938685c_fk_escola_disciplina_id` FOREIGN KEY (`disciplina_id`) REFERENCES `escola_disciplina` (`id`),
  CONSTRAINT `escola_nota_matricula_id_cbae3eaa_fk_escola_matricula_id` FOREIGN KEY (`matricula_id`) REFERENCES `escola_matricula` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `escola_nota`
--

LOCK TABLES `escola_nota` WRITE;
/*!40000 ALTER TABLE `escola_nota` DISABLE KEYS */;
/*!40000 ALTER TABLE `escola_nota` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `escola_professor`
--

DROP TABLE IF EXISTS `escola_professor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `escola_professor` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nome` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `telefone` varchar(20) DEFAULT NULL,
  `especialidade` varchar(100) DEFAULT NULL,
  `data_admissao` date NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `escola_professor`
--

LOCK TABLES `escola_professor` WRITE;
/*!40000 ALTER TABLE `escola_professor` DISABLE KEYS */;
/*!40000 ALTER TABLE `escola_professor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `escola_turma`
--

DROP TABLE IF EXISTS `escola_turma`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `escola_turma` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) NOT NULL,
  `semestre` varchar(20) NOT NULL,
  `turno` varchar(10) NOT NULL,
  `curso_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `escola_turma_curso_id_cba0213d_fk_escola_curso_id` (`curso_id`),
  CONSTRAINT `escola_turma_curso_id_cba0213d_fk_escola_curso_id` FOREIGN KEY (`curso_id`) REFERENCES `escola_curso` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `escola_turma`
--

LOCK TABLES `escola_turma` WRITE;
/*!40000 ALTER TABLE `escola_turma` DISABLE KEYS */;
/*!40000 ALTER TABLE `escola_turma` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-22  9:41:23

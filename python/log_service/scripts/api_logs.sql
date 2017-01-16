DROP TABLE IF EXISTS `api_logs`;
CREATE TABLE `api_logs` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `organization` varchar(64) NOT NULL,
  `service` varchar(64) NOT NULL,
  `method` varchar(64) NOT NULL,
  `invoked_time` int(10) unsigned NOT NULL,
  `return_code` int(11) NOT NULL,
  `frequency` int(10) unsigned DEFAULT '1',
  `request` varchar(8192) DEFAULT NULL,
  `response` varchar(8192) DEFAULT NULL,
  `project` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unq_index` (`organization`,`service`, `method`,`return_code`,`invoked_time`, `project`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

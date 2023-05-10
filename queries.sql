CREATE TABLE `tasks` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(255) NOT NULL,
	`jobName` VARCHAR(255) NOT NULL,
	`status` TINYINT NOT NULL DEFAULT '0',
	`result_filename` VARCHAR(255),
	PRIMARY KEY (`id`),
	FOREIGN KEY (jobName) REFERENCES jobs(name) ON DELETE CASCADE
);


CREATE TABLE `jobs` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(255) NOT NULL UNIQUE,
	`status` TINYINT NOT NULL DEFAULT '0',
	`date` DATETIME NOT NULL,
	PRIMARY KEY (`id`)
);
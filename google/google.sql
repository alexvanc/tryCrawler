DROP table if exists `google_topic`;
create table `google_topic`(
`id` bigint(20) NOT NULL AUTO_INCREMENT,
`topicid` varchar(128) NOT NULL UNIQUE,
`content` text,
`cnumber` int,
`vnumber` int,
`author` varchar(255),
`lasttime` timestamp,
primary key(`id`)
) ENGINE=InnoDB Default charset=utf8;

DROP table if exists `google_passage`;
create table `google_passage`(
`id` bigint(20) NOT NULL AUTO_INCREMENT,
`topicid` varchar(128) NOT NULL,
`passageid` varchar(128) NOT NULL UNIQUE,
`author` varchar(255),
`content` text,
primary key(`id`)
) ENGINE=InnoDB Default charset=utf8;


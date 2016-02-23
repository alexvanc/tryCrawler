DROP table if exists `git_issue`;
create table `git_issue`(
`id` bigint(20) NOT NULL AUTO_INCREMENT,
`issueid` bigint(20) NOT NULL UNIQUE,
`title` text,
`content` text,
`state` varchar(64),
`labels` varchar(255),
`comment_number` int,
`create_time` timestamp,
`close_time` timestamp,
primary key(`id`)
) ENGINE=InnoDB Default charset=utf8;

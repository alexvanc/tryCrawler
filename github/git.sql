DROP table if exists `git_issue`;
create table `git_issue`(
`id` bigint(20) NOT NULL AUTO_INCREMENT,
`issueid` bigint(20) NOT NULL UNIQUE,
`number` bigint(20) NOT NULL,
`title` text,
`content` text,
`state` varchar(64),
`labels` varchar(255),
`userid` bigint(20),
`comment_number` int,
`create_time` timestamp,
`close_time` timestamp,
primary key(`id`)
) ENGINE=InnoDB Default charset=utf8;

DROP table if exists `git_comment`;
create table `git_comment`(
`id` bigint(20) NOT NULL AUTO_INCREMENT,
`commentid` bigint(20) NOT NULL UNIQUE,
`issuenumber` bigint(20) NOT NULL,
`content` text,
`userid` bigint(20),
`create_time` timestamp,
primary key(`id`)
) ENGINE=InnoDB Default charset=utf8;

DROP table if exists `git_user`;
create table `git_user`(
`id` bigint(20) NOT NULL AUTO_INCREMENT,
`userid` bigint(20) NOT NULL UNIQUE,
`name` varchar(128),
`realname` varchar(255),
`company` varchar(255),
`location` varchar(255),
`email` varchar(255),
`bio` text,
`repo_number` int,
`gist_number` int,
`followers` int,
`following` int,
`site_admin` tinyint(1),
`type` varchar(128),
`create_time` timestamp,
primary key(id)
)ENGINE=InnoDB Default charset=utf8;

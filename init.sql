DROP table if exists `flow_question`;
create table `flow_question`(
 `id` bigint(20) not NULL AUTO_INCREMENT,
 `questionid` bigint(20) NOT NULL UNIQUE, 
 `title` text,
 `content` text,
 `tag` varchar(255),
 `tags` varchar(511),
 `userid` bigint(20),
 `view_count` int,
 `answer_count` int,
 `comment_count` int,
 `favorite_count` int,
 `score` int,
 `accepted_answer_id` bigint(20),
 `create_time` timestamp,
 `last_time` timestamp,
 primary key(`id`)  
 ) ENGINE=InnoDB Default charset=utf8;

DROP table if exists `flow_answer`;
create table `flow_answer`(
 `id` bigint(20) not NULL AUTO_INCREMENT,
 `answerid` bigint(20) NOT NULL UNIQUE, 
 `questionid` bigint(20) NOT NULL,
 `content` text,
 `userid` bigint(20),
 `comment_count` int,
 `is_accepted` tinyint(1),
 `score` int,
 `create_time` timestamp,
 `last_time` timestamp,
 primary key(`id`)  
 ) ENGINE=InnoDB Default charset=utf8;

DROP table if exists `flow_user`;
create table `flow_user`(
 `id` bigint(20) not NULL AUTO_INCREMENT,
 `userid` bigint(20) NOT NULL UNIQUE, 
 `reputation` int,
 `accept_rate` int,
 `is_employee` tinyint(1),
 #`create_time` timestamp,
 `bronze` int,
 `silver` int,
 `gold` int,
 primary key(`id`)  
 ) ENGINE=InnoDB Default charset=utf8;

DROP table if exists `flow_comment`;
create table `flow_comment`(
`id` bigint(20) not NULL AUTO_INCREMENT,
`commentid` bigint(20) NOT NULL UNIQUE,
`userid` bigint(20) NOT NULL,
`content` text,
`score` int,
`create_time` timestamp,
`postid` bigint(20),
`of_question` tinyint(1),
`questionid` bigint(20),
`answerid` bigint(20),
primary key(`id`)
)ENGINE=InnoDB Default charset=utf8;
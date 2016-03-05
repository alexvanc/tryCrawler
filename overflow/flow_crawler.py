#!/usr/bin/python
#coding=utf-8
import urllib2
import MySQLdb
from StringIO import StringIO
import gzip
import json
import datetime

class FlowCrawler(object):
	def __init__(self, keyword="docker",dbtype="mysql",dbname="crawler"):
		self.dbHelper= DBhelper(dbtype,dbname)
		self.keyword=keyword
		self.baseUrl="http://api.stackexchange.com/2.2/"
		self.logFile=open("/home/kliosvseyy/flow_log.txt","a+")

	def startCrawler(self, page=1,pagesize=10,order="desc",sort="creation"):
		flag=True
		while flag:
			flag=self.crawlQuestions(page,pagesize,order,sort)
			page=page+1
		self.logFile.close()
		self.dbHelper.close()

	def crawlQuestions(self, page=1,pagesize=100,order="desc",sort="creation"): 
		url=self.baseUrl+"search?page="+str(page)+"&pagesize="+str(pagesize)+"&order="+order+"&sort="+sort+"&tagged="+self.keyword+"&site=stackoverflow&filter=!OTEIfp*ik3aNfU064g3qEXyff2ncgYk0RKqFM6F*3T9"
		result=self.getContent(url)
		qList=result.get('items',[])
		for q in qList:
			self.processQuestion(q)
		if result.get('quota_remaining',1)==1:
			self.logFile.write("now:\t"+str(page)+"\t"+str(pagesize)+"\n")
			return False
		else:
			return result.get('has_more',False)
		
	def processQuestion(self,question):
		questionObj=Question()
		questionObj.id=question['question_id']
		questionObj.title=question.get('title',"fake")
		questionObj.body=question.get('body',"fake")
		questionObj.tag=self.keyword
		questionObj.tags=question.get('tags',[]) #value type is list
		owner=question.get('owner',{})
		questionObj.user_id=owner.get('user_id',0)
		questionObj.accepted_answer_id=question.get('accepted_answer_id',-10000)
		questionObj.view_count=question.get('view_count',-10000)
		questionObj.answer_count=question.get('answer_count',-10000)
		questionObj.comment_count=question.get('comment_count',-10000)
		questionObj.favorite_count=question.get('favorite_count',-10000)
		questionObj.score=question.get('score',-10000)
		questionObj.create_time=changeTSMP2Date(question['creation_date'])
		questionObj.last_time=changeTSMP2Date(question['last_activity_date'])
		#save this question to database
		self.dbHelper.saveQuestion(questionObj)
		#process the user of this question
		self.processUser(question['owner'])
		#process related comments on this question
		if question.get('comment_count',0)!=0:
			self.processComments(question.get('comments',[]),True,question['question_id'])
		#process related answers on this question
		if question.get('is_answered',False):
			self.processAnswers(question.get('answers',[]))

	
	def processAnswers(self,answers):
		for answer in answers:
			answerObj=Answer()
			answerObj.id=answer['answer_id']
			answerObj.question_id=answer['question_id']
			answerObj.body=answer.get('body',"fake")
			answerObj.is_accepted=answer.get("is_accepted",False)
			owner=answer.get('owner',{})
			answerObj.user_id=owner.get('user_id',0)
			answerObj.comment_count=answer.get('comment_count',-10000)
			answerObj.score=answer.get('score',-10000)
			answerObj.create_time=changeTSMP2Date(answer['creation_date'])
			answerObj.last_time=changeTSMP2Date(answer['last_activity_date'])
			#save this answer to database
			self.dbHelper.saveAnswer(answerObj)
			#process the user of this answer
			self.processUser(answer['owner'])
			#process related comments on this answer
			if answer.get('comment_count',0)!=0:
				self.processComments(answer.get('comments',[]),False,answer['answer_id'])

	def processComments(self,comments,of_question,iid):
		for comment in comments:
			commentObj=Comment()
			commentObj.id=comment['comment_id']
			commentObj.post_id=comment['post_id']
			commentObj.body=comment.get('body','fake')
			commentObj.score=comment.get('score',-10000)
			commentObj.create_time=changeTSMP2Date(comment['creation_date'])
			owner=comment.get('owner',{})
			commentObj.user_id=owner.get('user_id',0)
			commentObj.of_question=of_question
			if of_question:
				commentObj.question_id=iid
				commentObj.answer_id=0
			else:
				commentObj.answer_id=iid
				commentObj.question_id=0
			#save this comment to database
			self.dbHelper.saveComment(commentObj)
			#process the user of this comment
			self.processUser(comment['owner'])
	
	def processUser(self,user):
		userObj=User()
		userObj.id=user.get('user_id',0)
		if userObj.id==0:
			return False
		userObj.reputation=user.get('reputation',-10000)
		userObj.accept_rate=user.get('accept_rate',-10000)
		userObj.is_employee=user.get('is_employee',False)
		#userObj.create_time=user['creation_date']
		badge_counts=user.get('badge_counts',{})
		userObj.bronze=badge_counts.get('bronze',-10000)
		userObj.silver=badge_counts.get('silver',-10000)
		userObj.gold=badge_counts.get('gold',-10000)
		#save this user to database
		self.dbHelper.saveUser(userObj)
	

	def getContent(self,url):
		print url
		#record the crawl history and recovery
		#self.logFile.write(url+"\n")
		response=urllib2.urlopen(url)
		buf=StringIO(response.read())
		f=gzip.GzipFile(fileobj=buf)
		data=f.read()
		result=json.loads(data)
		response.close()
		return result

class Question(object):
	def __init__(self):
		pass
	def toInsertSQl(self):
		strSQL="insert into flow_question (questionid,title,content,tag,tags,userid,view_count,answer_count,comment_count,favorite_count, \
			score,accepted_answer_id,create_time,last_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" 
		#print str_SQL
		#strSQL="insert into flow_question(questionid,title,content,tag,tags,userid,view_count,answer_count,comment_count,favorite_count, \
		#	score,accepted_answer_id,create_time,last_time) values (%d,%s,%s,%s,%s,%d,%d,%d,%d,%d,%d,%d,%s,%s)"
		#print strSQL
		return strSQL

class Answer(object):
	def __init__(self):
		pass
	def toInsertSQl(self):
		strSQL="insert into flow_answer (answerid,questionid,content,userid,comment_count,is_accepted,score,create_time,last_time) \
				values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
		#print strSQL
		return strSQL

class Comment(object):
	def __init__(self):	
		pass
	def toInsertSQl(self):
		strSQL="insert into flow_comment (commentid,userid,content,score,create_time,postid,of_question,questionid,answerid) \
				values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
		#print strSQL
		return strSQL

class User(object):
	def __init__(self):	
		pass
	def toInsertSQl(self):
		strSQL="insert into flow_user (userid,reputation,accept_rate,is_employee,bronze,silver,gold) \
				values (%s,%s,%s,%s,%s,%s,%s)" 
		#print strSQL
		return strSQL

class DBhelper(object):
	def __init__(self,dbtype="mysql",dbname="crawler"):
		self.db=MySQLdb.connect("localhost","hello","test1234",dbname,charset="utf8")
		self.cursor=self.db.cursor()
		self.logFile=open("/home/kliosvseyy/database_log.txt","a+")

	def saveQuestion(self,question):
		try:
			if self.hasQuestion(question.id)==False:
				self.cursor.execute(question.toInsertSQl(),(question.id,question.title,question.body,question.tag,
					",".join(question.tags),question.user_id,question.view_count,question.answer_count,question.comment_count,
				 	question.favorite_count,question.score,question.accepted_answer_id,question.create_time,question.last_time))
				self.db.commit()
		except:
			self.logFile.write("write a question\t"+str(question.id)+"\n")
	def saveAnswer(self,answer):
		try:
			if self.hasAnswer(answer.id)==False:
				self.cursor.execute(answer.toInsertSQl(),((answer.id,answer.question_id,answer.body,answer.user_id,answer.comment_count,
					answer.is_accepted,answer.score,answer.create_time,answer.last_time)))
				self.db.commit()
		except:
			self.logFile.write("write a answer\t"+str(answer.id)+"\n")
	def saveComment(self,comment):
		try:
			if self.hasComment(comment.id)==False:
				self.cursor.execute(comment.toInsertSQl(),((comment.id,comment.user_id,comment.body,comment.score,comment.create_time,
					comment.post_id,comment.of_question,comment.question_id,comment.answer_id)))
				self.db.commit()
		except:
			self.logFile.write("write a comment\t"+str(comment.id)+"\n")
	def saveUser(self,user):
		try:
			if self.hasUser(user.id)==False:
				self.cursor.execute(user.toInsertSQl(),((user.id,user.reputation,user.accept_rate,user.is_employee,user.bronze,user.silver,user.gold)))
				self.db.commit()
		except:
			self.logFile.write("write a user\t"+str(user.id)+"\n")
	def hasQuestion(self,question_id):
		count=self.cursor.execute("select * from flow_question where questionid=%d" % (question_id))
		if int(count)==0:
			return False
		else:
			return True

	def hasAnswer(self,answer_id):
		count=self.cursor.execute("select * from flow_answer where answerid=%d" % (answer_id))
		if int(count)==0:
			return False
		else:
			return True

	def hasUser(self,user_id):
		count=self.cursor.execute("select * from flow_user where userid=%d" % (user_id))
		if int(count)==0:
			return False
		else:
			return True

	def hasComment(self,comment_id):
		count=self.cursor.execute("select * from flow_comment where commentid=%d" % (comment_id))
		if int(count)==0:
			return False
		else:
			return True

	def close(self):
		self.cursor.close()
		self.db.close()	
		self.logFile.close()

def changeTSMP2Date(timeStamp):
	return datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S')

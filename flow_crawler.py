#!/usr/bin/python
#coding=utf-8
import urllib2
import MySQLdb
from StringIO import StringIO
import gzip
import json

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
		questionObj.tags=question.get('tags',[]) #value type is list
		questionObj.user_id=question['owner']['user_id']
		questionObj.accepted_answer_id=question.get('accepted_answer_id',-10000)
		questionObj.view_count=question.get('view_count',-10000)
		questionObj.answer_count=question.get('answer_count',-10000)
		questionObj.comment_count=question.get('comment_count',-10000)
		questionObj.favorite_count=question.get('favorite_count',-10000)
		questionObj.score=question.get('score',-10000)
		questionObj.create_time=question['creation_date']
		questionObj.last_time=question['last_activity_date']
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
			answerObj.user_id=answer['owner']['user_id']
			answerObj.comment_count=answer.get('comment_count',-10000)
			answerObj.score=answer.get('score',-10000)
			answerObj.create_time=answer['creation_date']
			answerObj.last_time=answer['last_activity_date']
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
			commentObj.create_time=comment['creation_date']
			commentObj.user_id=comment['owner']['user_id']
			commentObj.of_question=of_question
			if of_question:
				commentObj.question_id=iid
			else:
				commentObj.answer_id=iid
			#save this comment to database
			self.dbHelper.saveComment(commentObj)
			#process the user of this comment
			self.processUser(comment['owner'])
	
	def processUser(self,user):
		userObj=User()
		userObj.id=user['user_id']
		userObj.reputation=user.get('reputation',-10000)
		userObj.accept_rate=user.get('accept_rate',-10000)
		userObj.is_employee=user.get('is_employee',False)
		#userObj.create_time=user['creation_date']
		badge_counts=user.get('badge_counts',{})
		userObj.bronze=badge_counts.get('bronze',-10000)
		userObj.bronze=badge_counts.get('silver',-10000)
		userObj.bronze=badge_counts.get('gold',-10000)
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
		pass

class Answer(object):
	def __init__(self):
		pass
	def toInsertSQl(self):
		pass

class Comment(object):
	def __init__(self):	
		pass
	def toInsertSQl(self):
		pass

class User(object):
	def __init__(self):	
		pass
	def toInsertSQl(self):
		pass

class DBhelper(object):
	def __init__(self,dbtype="mysql",dbname="crawler"):
		self.db=MySQLdb.connect("localhost","hello","test1234",dbname)
		self.logFile=open("/home/kliosvseyy/database_log.txt","a+")

	def saveQuestion(self,question):
		self.logFile.write("write a question"+"\n")
	def saveAnswer(self,answer):
		self.logFile.write("write a answer"+"\n")
	def saveComment(self,comment):
		self.logFile.write("write a comment"+"\n")
	def saveUser(self,user):
		self.logFile.write("write a user"+"\n")
	def hasQustion(self,question_id):
		return False
	def hasAnswer(self,answer_id):
		return False
	def hasUser(self,user_id):
		return False
	def hasComment(self,comment_id):
		return False
	def close():
		self.db.close()	
		self.logFile.close()

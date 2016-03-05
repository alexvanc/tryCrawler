#!/usr/bin/python
#coding=utf-8
import urllib2
import MySQLdb
from StringIO import StringIO
import gzip
import json
import datetime

class GitCrawler(object):
	def __init__(self, user='docker',repo='docker',term='issues',dbtype="mysql",dbname="crawler"):
		self.dbHelper= DBHelper(dbtype,dbname)
		self.baseUrl="https://api.github.com/repos/"+user+'/'+repo+'/'+term
		self.logFile=open("/home/kliosvseyy/git_log.txt","a+")

	def startCrawler(self,page=1,pagesize=100):
		flag=True
		while flag:
			flag=self.crawlIssues(page,pagesize)
			page=page+1
		self.logFile.close()
		self.dbHelper.close()
		pass
		
	def crawlIssues(self,page=1,pagesize=100):
		url=self.baseUrl+'?state=all&page='+str(page)+'&per_page='+str(pagesize)
		# print url
		result=self.getContents(url)
		counter=0
		for i in result:
			counter=counter+1
			issue=Issue()
			issue.id=i.get('id',-10000)
			issue.title=i.get('title','')
			issue.number=i.get('number',-10000)
			issue.content=i.get('body','')
			issue.commentNumber=i.get('comments',-10000)
			issue.state=i.get('state','')
			tempLables=i.get('labels',[])
			issue.label=[]
			for l in tempLables:
				issue.label.append(l.get('name',''))

			user=i.get('user',{})
			issue.userid=user.get('id',-10000)
			self.crawlUser(user.get('login',''),issue.userid)#crawl the user

			issue.createDate=changeTSMP2Date(i.get('created_at',''))
			issue.closeDate=changeTSMP2Date(i.get('closed_at',''))
			self.dbHelper.saveIssue(issue);

			pageIndex=1 #cralw the comment
			while self.crawlComments(issue.number,pageIndex,pagesize):
				pageIndex+=1

		if counter==pagesize:
			return True
		else:
			return False

	def crawlComments(self,number,page=1,pagesize=100):
		url=self.baseUrl+'/'+str(number)+'/comments'+'?page='+str(page)+'&per_page='+str(pagesize)
		result=self.getContents(url)
		counter=0
		for i in result:
			counter=counter+1
			comment=Comment(number)
			comment.commentID=i.get('id',-10000)
			comment.content=i.get('body','')

			user=i.get('user',{})
			comment.userid=user.get('id',-10000)
			self.crawlUser(user.get('login',''),comment.userid)#crawl the user

			comment.createDate=changeTSMP2Date(i.get('created_at',''))
			self.dbHelper.saveComment(comment)
		if counter==pagesize:
			return True
		else:
			return False

	def crawlUser(self,username,userid):
		if username=='' or self.dbHelper.hasUser(userid):
				return	
		url='https://api.github.com/users/'+username
		result=self.getContents(url)
		user=User(username,userid)
		user.type=result.get('type','')
		user.admin=result.get('site_admin',False)
		user.realname=result.get('name','')
		user.company=result.get('company','')
		user.location=result.get('location','')
		user.email=result.get('email','')
		user.bio=result.get('bio','')
		user.repoNumber=result.get('public_repos',-10000)
		user.gistNumber=result.get('public_gists',-10000)
		user.follower=result.get('followers',-10000)
		user.following=result.get('following',-10000)
		user.create_time=changeTSMP2Date(result.get('created_at',''))

		self.dbHelper.saveUser(user)



	def getContents(self,url):
		print url
		myheaders={'Authorization':'token e38fd0b6bb21775c244036772fe60724db3f0c31'}
		request=urllib2.Request(url,headers=myheaders)
		response=urllib2.urlopen(request)
		result=json.loads(response.read())
		# buf=StringIO(response.read())
		# f=gzip.GzipFile(fileobj=buf)
		# data=f.read()
		# result=json.loads(data)
		response.close()
		return result

class Issue(object):
	def __init__(self):
		pass
	
	def toInsertSQL(self):
		strSQL="insert into git_issue(issueid,number,title,content,userid,state,comment_number,labels,create_time,close_time) \
				values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" 
		return strSQL

class Comment(object):
	def __init__(self, number):
		self.number = number
	def toInsertSQL(self):
		strSQL="insert into git_comment(commentid,issuenumber,content,userid,create_time) values (%s,%s,%s,%s,%s)" 
		return strSQL

class User(object):
	def __init__(self, name,userid):
		self.name = name
		self.userid=userid
	def toInsertSQL(self):
		strSQL="insert into git_user(userid,name,realname,company,location,email,bio,repo_number,gist_number,followers,following,\
				site_admin,type,create_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
		return strSQL
			

class DBHelper(object):
	def __init__(self,dbtype="mysql",dbname="crawler"):
		self.db=MySQLdb.connect("localhost","hello","test1234",dbname,charset="utf8")
		self.cursor=self.db.cursor()
		self.logFile=open("/home/kliosvseyy/database_log.txt","a+")

	def saveIssue(self,issue):
		# try:
		if self.hasIssue(issue.id)==False:
			self.cursor.execute(issue.toInsertSQL(),(issue.id,issue.number,issue.title,issue.content,issue.userid,issue.state,issue.commentNumber,
				",".join(issue.label),issue.createDate,issue.closeDate))
			self.db.commit()
		# except:
		# 	self.logFile.write("write a issue\t"+str(issue.id)+"\n")

	def hasIssue(self,issueid):
		count=self.cursor.execute("select * from git_issue where issueid=%d" % (issueid))
		if int(count)==0:
			return False
		else:
			return True

	def saveComment(self,comment):
		# try:
		if self.hasComment(comment.commentID)==False:
			self.cursor.execute(comment.toInsertSQL(),(comment.commentID,comment.number,comment.content,comment.userid,comment.createDate))
			self.db.commit()
	# except:
		# 	self.logFile.write("write a comment failed in git\t"+str(comment.commentID))

	def hasComment(self,commentid):
		count=self.cursor.execute("select * from git_comment where commentid=%d" % (commentid))
		if int(count)==0:
			return False
		else:
			return True

	def saveUser(self,user):
		# try:
		if self.hasUser(user.userid)==False:
			self.cursor.execute(user.toInsertSQL(),(user.userid,user.name,user.realname,user.company,user.location,user.email,user.bio,
				user.repoNumber,user.gistNumber,user.follower,user.following,user.admin,user.type,user.create_time))
		# except:
		# 	self.logFile.write("write a user failed in git\t"+str(user.userid))

	def hasUser(self,userid):
		count=self.cursor.execute("select * from git_user where userid=%d" % (userid))
		if int(count)==0:
			return False
		else:
			return True

	def close(self):
		self.cursor.close()
		self.db.close()	
		self.logFile.close()

def changeTSMP2Date(isodate):
	if isodate=='' or isodate==None:
		return None
	else:
		return datetime.datetime.strptime(isodate,"%Y-%m-%dT%H:%M:%SZ").strftime('%Y-%m-%d %H:%M:%S')
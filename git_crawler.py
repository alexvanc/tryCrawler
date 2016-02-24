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
		self.logFile=open("/Users/yangyong/git_log.txt","a+")

	def startCrawler(self,page=1,pagesize=100):
		flag=True
		while flag:
			flag=self.crawlIssues(page,pagesize)
			page=page+1
		self.logFile.close()
		self.dbHelper.close()
		pass
		
	def crawlIssues(self,page=1,pagesize=100):
		url=self.baseUrl+'?page='+str(page)+'&per_page='+str(pagesize)
		print url
		result=self.getContents(url)
		counter=0
		for i in result:
			counter=counter+1
			issue=Issue()
			issue.id=i.get('id',-10000)
			issue.title=i.get('title','')
			issue.content=i.get('body','')
			issue.commentNumber=i.get('comments',-10000)
			issue.state=i.get('state','')
			tempLables=i.get('labels',[])
			issue.label=[]
			for l in tempLables:
				issue.label.append(l.get('name',''))
			issue.createDate=changeTSMP2Date(i.get('created_at',''))
			issue.closeDate=changeTSMP2Date(i.get('closed_at',''))
			self.dbHelper.saveIssue(issue);
		if counter==pagesize:
			return True
		else:
			return False

	def getContents(self,url):
		response=urllib2.urlopen(url)
		result=json.loads(response.read())
		# buf=StringIO(response.read())
		# f=gzip.GzipFile(fileobj=buf)
		# data=f.read()
		# result=json.loads(data)
		# response.close()
		return result

class Issue(object):
	def __init__(self):
		pass
	
	def toInsertSQL(self):
		strSQL="insert into git_issue(issueid,title,content,state,comment_number,labels,create_time,close_time) \
				values (%s,%s,%s,%s,%s,%s,%s,%s)" 
		return strSQL
		

class DBHelper(object):
	def __init__(self,dbtype="mysql",dbname="crawler"):
		self.db=MySQLdb.connect("localhost","hello","test1234",dbname,charset="utf8")
		self.cursor=self.db.cursor()
		self.logFile=open("/Users/yangyong/database_log.txt","a+")

	def saveIssue(self,issue):
		try:
			if self.hasIssue(issue.id)==False:
				self.cursor.execute(issue.toInsertSQL(),(issue.id,issue.title,issue.content,issue.state,issue.commentNumber,
					",".join(issue.label),issue.createDate,issue.closeDate))
				self.db.commit()
		except:
			self.logFile.write("write a issue\t"+str(issue.id)+"\n")

	def hasIssue(self,issueid):
		count=self.cursor.execute("select * from git_issue where issueid=%d" % (issueid))
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
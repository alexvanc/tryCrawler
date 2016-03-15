import MySQLdb
import numpy as np
import matplotlib.pyplot as plt


class DBhelper(object):
	def __init__(self,dbtype="mysql",dbname="crawler2"):
		self.db=MySQLdb.connect("localhost","root","mysqlyasin",dbname,charset="utf8")
		self.cursor=self.db.cursor()
		# self.logFile=open("/home/kliosvseyy/database_log.txt","a+")


	def counterFlowUser(self,date1,date2):
		userDict={}
		strSQL="select userid from flow_question where create_time>='%s' and create_time <'%s'" % (date1,date2)
		self.cursor.execute(strSQL)
		results=self.cursor.fetchall()
		for result in results:
			if userDict.has_key(result[0]):
				pass
			else:
				userDict[result[0]]=1

		strSQL="select userid from flow_answer where create_time>='%s' and create_time <'%s'" % (date1,date2)
		self.cursor.execute(strSQL)
		results=self.cursor.fetchall()
		for result in results:
			if userDict.has_key(result[0]):
				pass
			else:
				userDict[result[0]]=1

		strSQL="select userid from flow_comment where create_time>='%s' and create_time <'%s'" % (date1,date2)
		self.cursor.execute(strSQL)
		results=self.cursor.fetchall()
		for result in results:
			if userDict.has_key(result[0]):
				pass
			else:
				userDict[result[0]]=1
		

		print len(userDict)
		self.close()



	def counterGitUser(self,date1,date2):
		userDict={}

		strSQL="select userid from git_issue where create_time>='%s' and create_time <'%s'" % (date1,date2)
		self.cursor.execute(strSQL)
		results=self.cursor.fetchall()
		for result in results:
			if userDict.has_key(result[0]):
				pass
			else:
				userDict[result[0]]=1

		strSQL="select userid from git_comment where create_time>='%s' and create_time <'%s'" % (date1,date2)
		self.cursor.execute(strSQL)
		results=self.cursor.fetchall()
		for result in results:
			if userDict.has_key(result[0]):
				pass
			else:
				userDict[result[0]]=1
		

		print len(userDict)
		self.close()

	def counterGoogleUser(self,date1,date2,group):
		userDict={}

		strSQL="select author,topicid from %s_topic where lasttime>='%s' and lasttime <'%s'" % (group,date1,date2)
		self.cursor.execute(strSQL)
		results=self.cursor.fetchall()
		for result in results:
			if userDict.has_key(result[0]):
				pass
			else:
				userDict[result[0]]=1

			strSQL="select author from %s_passage where topicid='%s'" % (group,result[1])
			self.cursor.execute(strSQL)
			results2=self.cursor.fetchall()
			for result2 in results2:
				if userDict.has_key(result2[0]):
					pass
				else:
					userDict[result2[0]]=1
			

		print len(userDict)
		self.close()

	def plotPic(self):
		x = np.linspace(0, 10, num=100)
		y = np.sin(x)
		plt.plot(x,y)
		plt.show()

		self.close()

	def close(self):
		self.cursor.close()
		self.db.close()
		pass

# DBhelper().counterFlowUser('2013-01-01', '2017-01-01')
# DBhelper().counterGitUser('2013-01-01', '2017-01-01')
# DBhelper().counterGoogleUser('2013-01-01', '2017-01-01','google')
DBhelper().plotPic()
#!/usr/bin/python
#coding=utf-8
import MySQLdb
from sgmllib import SGMLParser
import re
import urllib
import urllib2


class GroupCrawler(SGMLParser):
	
	def startCrawler(self,keyword="docker",dbtype="mysql",dbname="crawler"):
		# print self.baseContent
		self.dbHelper= DBhelper(dbtype,dbname)
		self.keyword=keyword
		#根据一个基本的群组信息网页来抓取其他数据
		baseFile=open("/Users/yangyong/Downloads/docker-user.html","r")
		self.baseContent=baseFile.read()
		baseFile.close()
		self.baseUrl='https://groups.google.com/forum/#!topic/docker-user/'
		self.logFile=open("/Users/yangyong/group_user_log.txt","a+")

		self.inNumberSpan=0
		self.inAnthorDiv=False
		self.inTopicA=False
		self.currentTopic=Topic()

		self.feed(self.baseContent)
		self.logFile.close()
		self.dbHelper.close()

	def start_div(self,attrs):
		for k,v in attrs:
			if k=='class' and v=='IVILX2C-pb-b':
				self.inAnthorDiv=True
		pass
						
		
	def end_div(self):
		pass
	def start_span(self,attrs):
		if len(attrs)==1:
			for k,v in attrs:
				if k=='class' and v=='IVILX2C-pb-r':
					self.inNumberSpan+=1
				elif k=='title':
					self.currentTopic.lastTime=v
					self.currentTopic.processTime()
					self.crawlTopic(self.currentTopic.rawID)
					self.dbHelper.saveTopic(self.currentTopic)
					# print self.currentTopic.rawID,v
	def start_a(self,attrs):
		tag=False
		for k,v in attrs:
			if k=='class' and v=='IVILX2C-p-Q':
				tag=True
			elif tag and k=='id':
				self.currentTopic.rawID=v
				self.currentTopic.processID()
				# print v
				self.inTopicA=True
				tag=False

	def start_script(self,attrs):
		self.literal=1#不处理script标签，解析库会产生bug

	def handle_data(self,text):
		if self.inTopicA:
			self.currentTopic.content=text
			self.inTopicA=False
		elif self.inAnthorDiv:
			self.currentTopic.author=text
			self.currentTopic.processAuthor()
			self.inAnthorDiv=False
			# print text
		elif self.inNumberSpan==1:
			if text.strip()!='':
				self.currentTopic.cNumber=text
				self.currentTopic.processCNumber()
				# print 'comment', text
		elif self.inNumberSpan==2:
			self.currentTopic.vNumber=text
			self.currentTopic.processVNumber()
			self.inNumberSpan=0
			# print '2'
			# self.dbHelper.saveTopic(self.currentTopic)
			# print 'view',text

	def crawlTopic(self, rawTopicID):
		self.dbHelper=DBhelper()
 		# pass
		if rawTopicID.strip()=='':
			pass
		elif self.dbHelper.hasTopic(rawTopicID)==True:
			pass
		else:
			# print rawTopicID
			pCounter=0
			counter=0
			currentPassage=Passage(rawTopicID)
			result=self.getContent(rawTopicID)
			try:
				for item in result:
					counter=counter+1
					if (re.match(r'[a-zA-Z0-9_-]{12}', item) and (len(item)==12 or item[12]=='"')) or (item=='6m'):
						# print item
						if len(item)!=12 and item!='6m':
							# print 'hehe'
							item=item.split('"')[0]
						if pCounter==0:
							pCounter=1
							currentPassage.content=result[counter]
						elif pCounter==1:
							pCounter=2
							currentPassage.passageID=item
							self.dbHelper.savePassage(currentPassage)
							currentPassage.content=result[counter+1]
						elif pCounter==2:
							pCounter=3
							currentPassage.passageID=item
							self.dbHelper.savePassage(currentPassage)
							currentPassage.content=result[counter+1]
						elif pCounter==3:
							currentPassage.passageID=item
							self.dbHelper.savePassage(currentPassage)
							currentPassage.content=result[counter]
						else:
							print "A problem "+rawTopicID+" "+item
			except:
				print "array out"




			# print result
		# print self.baseUrl+self.currentTopic.processID()

	def getContent(self,rawTopicID):
		cookie='HSID=AdGSDjh9xahk54Lcs; SSID=Al72IXcOZsk98Uu8k; APISID=mHn9H2F1BVKrl4ed/AOOezNf0ZMz_4dlcH; SAPISID=ItlgSLJ1tffOzPlL/AVy2KrJVRBLwPYNuL; groupsloginpref=aEiIwOuxfzdCmLZe4oB1JsBmCUxwG8x-u-HBCV9JT8E=kliosvseyy@gmail.com; NID=77=gVzpiep6YPNKjJwwQIAJq2yQEoGDu5DK14tpSKB38JMXB80LmnNRQ1IX84S_oxg2GCHB5o9MJJ346nGpFJiS5UysJMryRoHZqTHcVMnMD_Ut1RnLtI5vX-hyi8BP3H-Fyr14HUacPnJQ4oRjmdVHKkWXvKJJtnhXxnxQJeQgvQ8tTpLnG0FXkM1BdoNfrnVKWZzKOjonlQ; SID=DQAAACQBAAD8yuIrg0DmZRtZ18_83TFtBNpPsrTAkzLBfsCVaHEatgmSAASVySKLFAnyXzggLUmatiAf-Kx_Xs-vL3TDF5BHuvvzW1CSdxPpuQzUVbL5LuRmv3DJZb6QOf8CHkuIzczmJ4ThGRFsb8pE08m01Zs0gWV1zfQt_Sn6ADsbdloLHRREw02UR5mGaQenj1GNmBuOsRgCjgMQHXOQ29xeeUMrW53m01xvQgtTZTRYtbAEvzQLP-i82BglDdM3tjox4onkXjOze0E9P1Id3xVjEOSe2imKEw1dmYMZQsTny74YQGaDyhHhoXn-lVbLh961zyuqWgU00j8rQl4kc8vkAJ-T3N3Xvc1_eqACvx_p6IcSdSC_Q-8AcbFJhVP26mLWDd9uRZMdheB_UJZaVv8h31Og; __utmt_*groups_ga*=1; __utma=118165087.1320653427.1449388955.1456589711.1456589711.31; __utmb=118165087.4.10.1456589711; __utmc=118165087; __utmz=118165087.1456561832.21.11.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)'
		self.baseUrl='https://groups.google.com/forum/msg_bkg?appversion=1&hl=zh-CN&authuser=0'
		myheaders={
		'x-client-data':'CKO2yQEIwbbJAQj9lcoBCIqXygE=',
		# ':authority':'groups.google.com',
		# ':method':'POST',
		'cookie':cookie,
		'x-groups-group-name':'docker-user',
		# ':path':'/forum/msg_bkg?appversion=1&hl=zh-CN&authuser=0',
		# ':scheme':'https',
		'accept-language':'zh-CN,zh;q=0.8',
		'content-type':'text/x-gwt-rpc; charset=UTF-8',
		'x-gwt-permutation':'223962F3B73B5E26DD33624701419784'
		}
		postdata='7|3|15|https://groups.google.com/forum/|D3EC77A6D699DC80502787E6A345082A|6p|AKUva6olU8u8wB7iiHZIcqtgfLZ-pQJksA:1456589710579|_|getMessagesAndExtraInfoForTopics|k|5u|6y|Z|2i|docker-user|6h|18|%s|1|2|3|4|5|6|6|7|8|9|10|11|10|7|12|12|0|0|13|14|500|0|15|0|0|0|0|' % (rawTopicID)
		request=urllib2.Request(self.baseUrl,data=postdata,headers=myheaders)
		# request.add_data(urllib.urlencode(postdata))
		# for k,v in headers:
		# 	request.add_header(k, v)
		# print self.baseUrl
		response=urllib2.urlopen(request)
		result=response.read()

		result=result.replace('\\x3C','<')
		result=result.replace('\\x3E','>')
		result=result.replace('\\x3D','=')
		result=result.replace('\\x27','\'')
		result=result.replace('\\x26','&')
		result=re.sub(r'<[^\'>]+>',' ',result)
	
		return result.split('","')
		
class Topic(object):
	def __init__(self):
		pass
	def processID(self):
		result=self.rawID.split('_',3)
		self.rawID=result[3]
		return result[3]	
	def processTime(self):
		stime=re.sub(r'[^a-zA-Z0-9]+', ' ', self.lastTime)
		tlist=stime.split(' ')
		self.lastTime=tlist[0]+'-'+tlist[1]+'-'+tlist[2]+' '+tlist[5]+':'+tlist[6]+':'+tlist[7]
		return self.lastTime
		# print self.rawID+'\n'
	def processCNumber(self):
		self.cNumber=re.search(r'[0-9]+', self.cNumber).group()
		return self.cNumber
	def processVNumber(self):
		self.vNumber=re.search(r'[0-9]+', self.vNumber).group()
		return self.vNumber
	def processAuthor(self):
		result=self.author.split('：')
		self.author=result[1]
		return result[1]
	def toInsertSQl(self):
		strSQL="insert into guser_topic(topicid,content,cnumber,vnumber,author,lasttime) values (%s,%s,%s,%s,%s,%s)" 
		return strSQL

class Passage(object):
	def __init__(self,topicID):
		self.topicID=topicID

	def toInsertSQl(self):
		strSQL="insert into guser_passage(topicid,passageid,content) values (%s,%s,%s)"
		return strSQL
		



class DBhelper(object):
	def __init__(self,dbtype="mysql",dbname="crawler"):
		self.db=MySQLdb.connect("localhost","hello","test1234",dbname,charset="utf8")
		self.cursor=self.db.cursor()
		self.logFile=open("/Users/yangyong/database_log.txt","a+")

	def saveTopic(self,topic):
		try:
			if self.hasTopic(topic.rawID)==False:
				self.cursor.execute(topic.toInsertSQl(),(topic.rawID,topic.content,topic.cNumber,topic.vNumber,
					topic.author,topic.lastTime))
				self.db.commit()
		except:
			self.logFile.write("write a topic\t"+str(topic.rawID)+"\n")

	def savePassage(self,passage):
		# print passage.passageID
		try:
			if self.hasPassage(passage.passageID)==False:
				self.cursor.execute(passage.toInsertSQl(),(passage.topicID,passage.passageID,passage.content))
				self.db.commit()
				print 'finish',passage.passageID
		except:
			self.logFile.write("write a passage\t"+str(passage.passageid)+"\n")



	def hasTopic(self,rawID):
		count=self.cursor.execute("select * from guser_topic where topicid='%s'" % (rawID))
		if int(count)==0:
			return False
		else:
			return True
	def hasPassage(self,passageid):
		count=self.cursor.execute("select * from guser_passage where passageid='%s'" % (passageid))
		# print str(int(count))
		if int(count)==0:
			return False
		else:
			return True
	def close(self):
		self.cursor.close()
		self.db.close()	
		self.logFile.close()

GroupCrawler().startCrawler()
# GroupCrawler().crawlTopic('ypJsDNU7A40')
# testFile=open("/Users/yangyong/Downloads/test.html","r")
# PassageParser().startAnalyze(testFile.read(),'yy')
# testFile.close()
# GroupCrawler().crawlTopic('D2qdrik49Qw')


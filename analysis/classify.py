#!/usr/bin/python
#coding=utf-8
import re
from collections import Counter
import MySQLdb


testDict={'docker':['go','run','daemon','api','boot','exec','engine','expose','log','config','configuration','lxc',' restart','  isolation',' permission',' permissions',' layer','bridge','linked','link','attach','priviledged','security','bind',' overlay',' mapping',' status','dns','devie',' network','networks','map','archive','snaphost',' qemu'],
			'os':['bash','commandline','cmd','ubuntu','linux','system','root','windows','shell','address','apt','sudo','kernel','filesystem','memory','pid','debian','storage','mounted','library','space','os','mac','sock','top','cpu','hostname','namespace','unix','iptables','resources','coreos','systemd','centos','socket',' devicemapper','chmod',' yum',' fedora','redhat','vivid','cgroup','photon','atomic'],
			'orchestration':['swarm','compose','	machine','nginx','kurbernetes','driver','drivers','distribution','mesos','mesosphere','cluster','zookeeper','orchestration'],
			'platform':['amazon','aws','google','heroku','dotcloud','tutum','azure','ec2'],
			'image':['pull','image','images','build','builds','run','dockerfile','add','regitry','hub','exec','service','entrypoint','inspect','commit',' tag','show','export','repository','delete','baseimage','entrypoin'],
			'application':['web','virtualbox','apache','git','python','posgres','db','php','database',' java','tomcat','posgresql','maven','mongo','mongodb','node.js','busybox','wordpress','pip','jar',' elasticseatch','rabbitmq','toolbox','sql','cassandra'],
			'other':['tcp','varialbles','redis','stack','tmp','supervisor','virtual','json','output','setup','production','curl','interface','launch','debug','discovery','package','backup','depolyment','download','deploy',' admin',' virtualization','weave']}
resultlist=[0,0,0,0,0,0,0]
# print 'Words in text:', len(word_list)

# #delete stop words like "a,the,that"
# def delStopWords():
# 	pass

# #generate a frequency dict for each term
# def getFrequencyDic(text):
# 	punctuation = re.compile(r'[.?!,":;>()/-_{}]|[0-9]*') 
# 	text=punctuation.sub(" ", word)
# 	word_list = re.split('\s+', text.lower())
# 	freq_dic = {}
# 	for word in word_list:
# 	    # form dictionary
# 	    try: 
# 	        freq_dic[word] += 1
# 	    except: 
# 	        freq_dic[word] = 1
	    
# 	print 'Unique words:', len(freq_dic)
# 	return freq_dic


# #sort by the frequency and print the result
# def sortAndPrint(freq_dic,limit):
	
# def analyzeSource(source,pagesize):
# 	pass
guser=['Jérôme Petazzoni','James Mills','Solomon Hykes','Sven Dowideit','Jessica Frazelle','nicolas de loof','Tianon,Michael Neale','Sebastiaan van Stijn','James Turnbull']
guuser=['Jérôme Petazzoni','Sven Dowideit','Solomon Hykes','James Mills','Aidan Hobson Sayers','Ian Miell','jude m','Michael Neale','abilash ks','Daniel YC Lin']
ouser=['6309','2915097','4332','107049','256618','147356','448734','706727','444646','884978']
gituser=['1032519','749551','28492','1445228','161631','101445','799078','1804568','29565','1050']
class SourceAnalyzer(object):
	def __init__(self, source):
		self.source = source
		self.dbHelper=DBHelper()
		self.stopWords=['com','docker','https','have','the','github','be','could','it','he','a','an','the','this','that','to','in','at','on','of','and','not','with','or','for','by','as','if','when','for','is','from','into','onto','','my','you','']

	def startAnalyzer(self,limit,pagesize=0):
		if pagesize==0:
			results=self.dbHelper.getContent(self.source, False, pagesize)
		else:
			results=self.dbHelper.getContent(self.source, True, pagesize)
		for result in results:
			self.split(result)

		print resultlist
	def startAnalyzerWithSQL(self,limit,SQL):
		
		results=self.dbHelper.excuteSQL(SQL)
		freq_dict={}
		for result in results:
			freq_dict=self.mergeDicts(freq_dict,self.preprocess(result))
		self.sortAndPrint(freq_dict, limit)


	def split(self,text):
		punctuation = re.compile(r'[.?!,":;>()/\[\]\-_&\'+=`#{}<>]|[0-9]+') 
		text=punctuation.sub(" ", text)
		word_list = re.split('\s+', text.lower())
		# print word_list
		counter=0
		templist=[0,0,0,0,0,0,0,0]
		for word in word_list:
			if word in self.stopWords:
				del word_list[counter]
			else:
				index=self.predictword(word)
				# print index
				templist[index]+=1
			counter+=1
		# print word_list

		maxNum=templist[0]
		maxindex=0
		for index in xrange(0,7):
			if templist[index]>maxNum:
				maxNum=templist[index]
				maxindex=index

		resultlist[maxindex]+=1
		return word_list

	def predictword(self,word):
		# templist=[0,0,0,0,0,0,0]
		counter=0;
		for k,v in testDict.items():
			if word in v:
				# print 'heeh'
				return counter
			counter+=1
		return 7


	def sortAndPrint(self,freq_dic,limit):
		freq_list=sorted(freq_dic.items(),key=lambda d:d[1], reverse=True)
		for word, freq in freq_list:
			try:
				print word, freq
				if freq<=limit:
					return
			except:
				pass
	# def getTermFromDB(self,pagesize):

		
	def preprocess(self,text):
		# punctuation = re.compile(r'[.?!,":;>()/-_{}]|[0-9]*') 
		try:
			punctuation = re.compile(r'[.?!,":;>()/\[\]\-_&\'+=`#{}<>]|[0-9]+') 
			text=punctuation.sub(" ", text)
			word_list = re.split('\s+', text.lower())
			freq_dic = {}
			for word in word_list:
			    # form dictionary
			    if word in self.stopWords:
			    	continue
			    try: 
			        freq_dic[word] += 1
			    except: 
			        freq_dic[word] = 1
			    
			# print 'Unique words:', len(freq_dic)
			return freq_dic
		except:
			return {}

	#merge 2 freq dict
	def mergeDicts(self,dic1,dic2):
		return dict(Counter(dic1)+Counter(dic2))

class DBHelper(object):
	def __init__(self, dbtype="mysql",dbname="crawler2"):
		self.db=MySQLdb.connect("localhost","root","mysqlyasin",dbname,charset="utf8")
		self.cursor=self.db.cursor()
		self.logFile=open("/Users/yangyong/database_log.txt","a+")

	def getContent(self,source,isLimited,number):
		results=[]
		strSQL=''
		if source=='overflow':
			temp=','.join(ouser)
			
			sql1="select title,content from flow_question"
			
			self.cursor.execute(sql1)
			tempResult=self.cursor.fetchall()
			for result in tempResult:
				results.append(result[0]+' '+result[1])
			
			return results
		elif source=='github':
			sql1="select title ,content from git_issue"
			self.cursor.execute(sql1)
			tempResult=self.cursor.fetchall()
			for result in tempResult:
				if result[0] is None or result[1] is None:
					results.append(" "+" "+" ")
				else:
					results.append(result[0]+" "+result[1])

			return results
		elif source=='google':
			sql1="select content,topicid from guser_topic"
			self.cursor.execute(sql1)
			tempResult=self.cursor.fetchall()
			for result in tempResult:
				results.append(result[0])
			# print sql1
			
			return results
		else:
			strSQL='select title,content from flow_question '

		if isLimited:
			strSQL+='limit '+str(number)
		self.cursor.execute(strSQL)
		tempResult=self.cursor.fetchall()
		for result in tempResult:
			results.append(result[0])
		return results

	def excuteSQL(self,SQL):
		results=[]
		self.cursor.execute(SQL)
		tempResult=self.cursor.fetchall()
		for result in tempResult:
			results.append(result[0])
			# results.append(result[1])
		return results
	def getDictBySQL(self,SQL):
		results={}
		self.cursor.execute(SQL)
		tempResult=self.cursor.fetchall()
		for result in tempResult:
			results.setdefault(str(result[0]),result[1])
		# print results
		return results
    	

	def close(self):
		self.cursor.close()
		self.logFile.close()
		self.db.close()

analyzer=SourceAnalyzer("google")
analyzer.startAnalyzer(2)

# analyzer=SourceAnalyzer("google")
# analyzer.startAnalyzerWithSQL(160,"select content from git_comment where create_time>'2016-01-01' and create_time<'2017-01-01'")


# analyzer=SourceAnalyzer("google")
# analyzer.startAnalyzerWithSQL(16,"select content from git_comment where create_time>'2016-01-01' and create_time<'2017-01-01'")


# analyzer=SourceAnalyzer("google")
# analyzer.startAprioriWithSQL(160,"select id, content from google_passage limit 500")
		
# # create list of (key, val) tuple pairs
# freq_list = freq_dic.items()
# # sort by key or word
# freq_list.sort()
# # display result

#code to be tested
# >>>
# >>>dict(Counter(x)+Counter(y))

# def f():
#     i = 0
#     while 1:
#         if i == 10000:
#             break
#         for k, v in y.items():
#             if k in x.keys():
#                 x[k] += v
#             else:
#                 x[k] = v
#         i += 1


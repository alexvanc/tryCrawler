#!/usr/bin/python
#coding=utf-8
import re
from collections import Counter
import MySQLdb
import apriori

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

	def startAnalyzer(self,limit):
		results=self.dbHelper.getContent(self.source)
		freq_dict={}
		for result in results:
			freq_dict=self.mergeDicts(freq_dict,self.preprocess(result))
		self.sortAndPrint(freq_dict, limit)

	def startAnalyzerWithSQL(self,limit,SQL):
		
		results=self.dbHelper.excuteSQL(SQL)
		freq_dict={}
		for result in results:
			freq_dict=self.mergeDicts(freq_dict,self.preprocess(result))
		self.sortAndPrint(freq_dict, limit)

	#用于挖掘频繁项集
	def startAprioriWithSQL(self,limit,SQL):
		resultDict=self.dbHelper.getDictBySQL(SQL)
		# dataDict={}
		# print resultDict
		for k,v in resultDict.items():
			resultDict[k]=self.split(v)

		# print resultDict
		tool=apriori.Apriori(dataDic=resultDict)
		result=tool.do()
		# print result
		for item in result:
			if len(item)>=2:
				print item
		# for k,v in result.items():
		# 	if v>=2:
		# 		print k

	def split(self,text):
		punctuation = re.compile(r'[.?!,":;>()/\[\]\-_&\'+=`#{}<>]|[0-9]+') 
		text=punctuation.sub(" ", text)
		word_list = re.split('\s+', text.lower())
		# print word_list
		counter=0
		for word in word_list:
			if word in self.stopWords:
				del word_list[counter]
			counter+=1
		# print word_list
		return word_list

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

	def getContent(self,source):
		results=[]
		strSQL=''
		temp=",".join(gituser)
		sql1="select title ,content from git_issue where userid IN (select userid from git_user where company like '%%%s%%')" % source
		sql2="select content from git_comment where userid IN (select userid from git_user where company like '%%%s%%')" % source
		self.cursor.execute(sql1)
		tempResult=self.cursor.fetchall()
		for result in tempResult:
			if result[0] is None or result[1] is None:
				results.append(" "+" "+" ")
			else:
				results.append(result[0]+" "+result[1])

		self.cursor.execute(sql2)
		tempResult2=self.cursor.fetchall()
		for result2 in tempResult2:
			results.append(result2[0])
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
analyzer.startAnalyzer(4)

# analyzer=SourceAnalyzer("google")
# analyzer.startAnalyzerWithSQL(160,"select content from git_comment where create_time>'2016-01-01' and create_time<'2017-01-01'")


# analyzer=SourceAnalyzer("google")
# analyzer.startAnalyzerWithSQL(16,"select content from git_comment where create_time>'2016-01-01' and create_time<'2017-01-01'")


# analyzer=SourceAnalyzer("google")
# analyzer.startAprioriWithSQL(160,"select id,content from git_comment limit 50")
		
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


#!/bin/python
#coding=utf-8
import re
import MySQLdb

#主要用来将网页标签和js代码去掉,<code>暂时保留，分别分析保留不保留的结果
class Processor():
	"""docstring for Processor"""
	def __init__(self, dbtype="mysql",dbname="crawler"):
		self.db=MySQLdb.connect("localhost","hello","test1234",dbname,charset="utf8")
		self.cursor=self.db.cursor()

	def startProcessor(self):
		self.changeContent('google_topic')
		self.changeContent('google_passage')
		self.changeContent('guser_topic')
		self.changeContent('guser_passage')
		self.changeContent('flow_question')
		self.changeContent('flow_answer')
		self.changeContent('flow_comment')
		self.changeContent('git_issue')
		self.changeContent('git_comment')


		self.close()

	def changeContent(self,table):
		sql="select id,content from %s" % table
		self.cursor.execute(sql)
		tempResult=self.cursor.fetchall()
		for result in tempResult:
			index=result[0]
			content=self.process(result[1])
			sql="update %s set content='%s' where id=%s" % (table,content,index)
			self.db.commit()
		print 'finish %s' % table

	def process(self,text):
		if text is None:
			return
		text=text.replace('<code>', '$code$')
		text=text.replace('</code>', '$/code$')
		pattern=re.compile(r'<[^>]+>')
		result=re.sub(pattern, ' ', text)
		content=result.replace('$code$', '<code>')
		content=content.replace('$/code$', '<code>')
		return content

	def close(self):
		self.cursor.close()
		self.db.close()

processor=Processor()
processor.startProcessor()
# print processor.process(test)



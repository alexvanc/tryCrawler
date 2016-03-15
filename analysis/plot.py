import datetime
from calendar import monthrange
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import MySQLdb

class Ploter(object):
	def __init__(self):
		self.db=MySQLdb.connect("localhost","root","mysqlyasin","crawler2",charset="utf8")
		self.cursor=self.db.cursor()

	def getDataFromDB(self):
		baseDate=datetime.date(2013,3,1)
		maxDate=datetime.date(2016,3,6)
		counter=(maxDate-baseDate).days
		print str(counter)
		# print baseDate.strftime('%Y-%m-%d'),nextDate.strftime('%Y-%m-%d')
		dateResult=[]
		numResult=[]
		for x in xrange(1,counter):
			# nextDate=baseDate+datetime.timedelta(days=monthrange(baseDate.year,baseDate.month)[1])
			nextDate=baseDate+datetime.timedelta(days=1)
			number=0
			sql1="select count(*) as number from flow_answer where create_time>='%s' and create_time<'%s'" % (baseDate.strftime('%Y-%m-%d'),nextDate.strftime('%Y-%m-%d'))
			sql2="select count(*) as number from flow_question where create_time>='%s' and create_time<'%s'" % (baseDate.strftime('%Y-%m-%d'),nextDate.strftime('%Y-%m-%d'))
			sql3="select count(*) as number from flow_comment where create_time>='%s' and create_time<'%s'" % (baseDate.strftime('%Y-%m-%d'),nextDate.strftime('%Y-%m-%d'))
			self.cursor.execute(sql1)
			results=self.cursor.fetchall()
			number+=results[0][0]
			self.cursor.execute(sql2)
			results=self.cursor.fetchall()
			number+=results[0][0]
			self.cursor.execute(sql3)
			results=self.cursor.fetchall()
			number+=results[0][0]
			dateResult.append(baseDate)
			numResult.append(number)
			baseDate=nextDate

		self.drawPic(dateResult, numResult)
		self.close()
		
	def drawPic(self,xdata,ydata):
		years    = mdates.YearLocator()   # every year
		months   = mdates.MonthLocator(interval=4)  # every month
		yearsFmt = mdates.DateFormatter('%Y')
		monthFmt = mdates.DateFormatter('%Y-%m')

		fig = plt.figure(dpi=110)
		ax = fig.add_subplot(111)
		ax.plot(xdata, ydata)

		# ax.xaxis.set_major_locator(years)
		# ax.xaxis.set_major_formatter(yearsFmt)
		# ax.xaxis.set_minor_locator(months)
		# ax.xaxis.set_minor_formatter(monthFmt)
		ax.xaxis.set_major_locator(months)
		ax.xaxis.set_major_formatter(monthFmt)

		
		datemin = datetime.date(2013, 2, 1)
		datemax = datetime.date(2016, 4, 1)
		ax.set_xlim(datemin, datemax)
		plt.xlabel('date')
		plt.ylabel('amount')

		temp=gca()
		for lable in temp.get_xticklabels() + temp.get_yticklabels() :
			lable.set_fontsize(10)

		# for lable in temp.get_xticklabels():
		# 	lable.set_fontsize(8)
		# for text in temp.get_xminorticklabels():
		# 	text.set_fontsize(8)
		# for text in temp.get_xmajorticklabels():
		# 	text.set_fontsize(8)

		# annotate('here',xy=(2015,))


		# ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
		ax.grid(True)

		# fig.autofmt_xdate()
		# plt.plot(xdata,ydata)
		plt.show()

	def close(self):
		self.cursor.close()
		self.db.close()

Ploter().getDataFromDB()


# years    = mdates.YearLocator()   # every year
# months   = mdates.MonthLocator()  # every month
# yearsFmt = mdates.DateFormatter('%Y')

# # load a numpy record array from yahoo csv data with fields date,
# # open, close, volume, adj_close from the mpl-data/example directory.
# # The record array stores python datetime.date as an object array in
# # the date column
# datafile = cbook.get_sample_data('goog.npy')
# r = np.load(datafile).view(np.recarray)

# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.plot(r.date, r.adj_close)


# # format the ticks
# ax.xaxis.set_major_locator(years)
# ax.xaxis.set_major_formatter(yearsFmt)
# ax.xaxis.set_minor_locator(months)

# datemin = datetime.date(r.date.min().year, 1, 1)
# datemax = datetime.date(r.date.max().year+1, 1, 1)
# ax.set_xlim(datemin, datemax)

# # format the coords message box
# def price(x): return '$%1.2f'%x
# ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
# ax.format_ydata = price
# ax.grid(True)

# # rotates and right aligns the x labels, and moves the bottom of the
# # axes up to make room for them
# fig.autofmt_xdate()

# plt.show() 
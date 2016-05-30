#!/usr/bin/python
#encoding=utf-8

import sys
import MySQLdb
import json

class DBUtil():
	"""
	操作db的工具
	"""
	def __init__(self, dbhost, dbport, dbname, username, password, charset='utf8'):
		self.host = dbhost
		self.port = dbport
		self.db = dbname
		self.user = username
		self.password = password
		self.charset = charset
		self.conn = MySQLdb.connect(host=dbhost, user=username, passwd=password, db=dbname, port=dbport, charset=charset)
		print "create a database connection to mysql"

	def __del__(self):
		self.conn.close()
		print "close the database connection to mysql"

	def close(self):
		self.conn.close()
		print "close the database connection to mysql"

	def query(self, sql):
		"""used for select"""
		result = {}
		try:
			cur = self.conn.cursor()
			cur.execute(sql)
			result = cur.fetchall()
			cur.close()
		except Exception as e:
			print "error, fail to execute %s: %s" % (sql, e)
			cur.close()
		return result

	def execute(self, sql):
		"""used for insert"""
		try:
			cur = self.conn.cursor()
			cur.execute(sql)
			self.conn.commit()
			cur.close()
		except Exception as e:
			print "error, fail to %s: %s" % (sql, e)
			cur.close()
			self.conn.close()
			self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, db=self.db, port=self.port, charset=self.charset)
			print "reconnect to mysql"
			cur = self.conn.cursor()
			cur.execute(sql)
			self.conn.commit()
			cur.close()

	def execute_batch(self, sql, args):
		"""
		insert multiple sets of data in batch.
		sql:  an sql sentence with parameters
		args: a list of data tuples
		"""
		try:
			cur = self.conn.cursor()
			cur.executemany(sql, args)
			self.conn.commit()
		except Exception as e:
			print "error, execute_batch %s failed: %s" % (sql, e)
		finally:
			cur.close()

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: ./db_util.py pre-release|production"
		sys.exit()
	
	if sys.argv[1] == "pre-release":
		print "pre-release"
		with open("../config/json.conf", 'r') as fd:
			conf = json.load(fd)
			dbhost = conf["pre-release"]["db"]["host"]
			dbport = conf["pre-release"]["db"]["port"]
			dbname = conf["pre-release"]["db"]["db_name"]
			user = conf["pre-release"]["db"]["user"]
			password = conf["pre-release"]["db"]["password"]

	elif sys.argv[1] == "production":
		print "production"
		with open("../config/json.conf", 'r') as fd:
			conf = json.load(fd)
			dbhost = conf["production"]["db"]["host"]
			dbport = conf["production"]["db"]["port"]
			dbname = conf["production"]["db"]["db_name"]
			user = conf["production"]["db"]["user"]
			password = conf["production"]["db"]["password"]

	else:
		print "invalid parameter"
		sys.exit()

	dbutil = DBUtil(dbhost, dbport, dbname, user, password)
	#sql = "select sum(frequency) from wmscronjob_logs where method = 'method4' and invoked_time >= 1462377600"
	#dataset = dbutil.query(sql)
	#if dataset[0][0] == None:
	#	print 0
	#else:
	#	print dataset[0][0]
	#sys.exit()

	sql = "insert into wmscronjob_logs(method, organization, service, invoked_time, return_code, request, response) values('binggo-method', 'pinhaohuo', 'self', 1462636920, 512, 'request', 'response') on duplicate key update frequency = frequency + 1"
	dbutil.execute(sql)
	del dbutil

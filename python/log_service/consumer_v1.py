#!/usr/bin/python
#encoding=utf-8

"""
Feature:
 * receive and parse the log from kafka cluster, then insert them to mysql.
"""

import sys
import os
import multiprocessing
import logging
import json
import time
import datetime
import MySQLdb
from pykafka import KafkaClient

from utils import logger
from utils import db_util
from utils import time_util


# configuration for kafka
kafka_hosts = ""
topic_name = ""
zk_hosts = ""

# configuration for db
dbhost = ""
dbport = 3306
dbname = ""
dbuser = ""
dbpasswd = ""

consumer_process_num = 2
log_dir = ""

def parse_msg(msg, log, dbutil):
	try:
		msg_obj = json.loads(msg)
	except Exception as e:
		log.error("unvalid json string: %s" % e)
		return

	if not msg_obj.has_key("organization"):
		log.error("absence of 'organization'")
		return
	organization = msg_obj["organization"]

	if not msg_obj.has_key("service"):
		log.error("absence of 'service'")
		return
	service = msg_obj["service"]

	if not msg_obj.has_key("method"):
		log.error("absence of 'method'")
		return
	method = msg_obj["method"]

	if msg_obj.has_key("timestamp"):
		invoked_time = msg_obj["timestamp"] # unix time, int
	else:
		invoked_time = int(time.time()) 

	if not msg_obj.has_key("error_code"):
		log.error("absence of 'error_code'")
		return
	return_code = int(msg_obj["error_code"])

	if not msg_obj.has_key("project"):
		log.error("absence of 'project'")
		return
	project = msg_obj["project"]
	
	request = ""
	if msg_obj.has_key("request"):
		request = msg_obj["request"]
	response = ""
	if msg_obj.has_key("response"):
		response = msg_obj["response"]
	
	# save the data into database
	table_name = project + "_logs"
	if return_code == 0:
		cur_day = datetime.date.today()
		start_time = time_util.unix_time(str(cur_day) + ' 00:00:00')
		sql = "insert into api_logs(organization, service, method, invoked_time, return_code, request, response, project) values(\"%s\", \"%s\", \"%s\", %d, %d, \"%s\", \"%s\", \"%s\") on duplicate key update frequency = frequency + 1" % (organization, service, method, start_time, return_code, MySQLdb.escape_string(request), MySQLdb.escape_string(response), project)
	else:
		sql = "insert into api_logs(organization, service, method, invoked_time, return_code, request, response, project) values(\"%s\", \"%s\", \"%s\", %d, %d, \"%s\", \"%s\", \"%s\") on duplicate key update frequency = frequency + 1" % (organization, service, method, invoked_time, return_code, MySQLdb.escape_string(request), MySQLdb.escape_string(response), project)
	log.debug(sql)
	dbutil.execute(sql)


def start_consume(seq):
	# initialization
	print "start the %dth consumer process" % (seq)
	client = KafkaClient(hosts=kafka_hosts)
	topic = client.topics[bytes(topic_name)]
	
	print "init logger for %dth consumer" % (seq)
	logger_name = "logstat.consumer.instance-" + str(seq)
	logger_file = log_dir + "/consumer-" + str(seq) + ".log"
	consumer_logger = logger.Logger(logger_name, logger_file, logging.DEBUG)
	
	print "init db for %dth consumer" % (seq)
	dbutil = db_util.DBUtil(dbhost, dbport, dbname, dbuser, dbpasswd)

	# consume message
	balanced_consumer = topic.get_balanced_consumer(
			consumer_group = "api_monitor_group",
			auto_commit_enable = True,
			zookeeper_connect = zk_hosts,
			num_consumer_fetchers = 2
		)
	print "consumer-%d has been ready to consume message" % (seq)

	for msg in balanced_consumer:
		if msg is not None:
			#print msg.value
			consumer_logger.debug(msg.value)
			parse_msg(msg.value, consumer_logger, dbutil)
	del dbutil


if __name__ == "__main__":
	if len(sys.argv) != 3:
		print "Usage: %s pre-release|production config_file" % (sys.argv[0])
		sys.exit()

	config_file = sys.argv[2]
	if os.path.exists(config_file) == False:
		print "config file given not exist"
		sys.exit()

	if sys.argv[1] == "pre-release":
		print "pre-release"
		with open(config_file, 'r') as fd:
			conf = json.load(fd)
			kafka_hosts = conf["pre-release"]["kafka"]["kafka_hosts"]
			topic_name = conf["pre-release"]["kafka"]["topic"]
			zk_hosts = conf["pre-release"]["kafka"]["zk_hosts"]
			dbhost = conf["pre-release"]["db"]["host"]
			dbport = conf["pre-release"]["db"]["port"]
			dbname = conf["pre-release"]["db"]["db_name"]
			dbuser = conf["pre-release"]["db"]["user"]
			dbpasswd = conf["pre-release"]["db"]["password"]
			log_dir = conf["pre-release"]["log"]["dir"]
	elif sys.argv[1] == "production":
		print "production"
		with open(config_file, 'r') as fd:
			conf = json.load(fd)
			kafka_hosts = conf["production"]["kafka"]["kafka_hosts"]
			topic_name = conf["production"]["kafka"]["topic"]
			zk_hosts = conf["production"]["kafka"]["zk_hosts"]
			dbhost = conf["production"]["db"]["host"]
			dbport = conf["production"]["db"]["port"]
			dbname = conf["production"]["db"]["db_name"]
			dbuser = conf["production"]["db"]["user"]
			dbpasswd = conf["production"]["db"]["password"]
			log_dir = conf["production"]["log"]["dir"]
	else:
		 print "invalid parameter"
		 sys.exit()
	
	if os.path.exists(log_dir) == False:
		print "log dir '%s' not exist" % (log_dir)
		sys.exit()

	pool = multiprocessing.Pool(processes=consumer_process_num)
	for i in xrange(consumer_process_num):
		pool.apply_async(start_consume, (i,)) # 跨进程传递的参数需要能被串行化
	pool.close()
	pool.join()

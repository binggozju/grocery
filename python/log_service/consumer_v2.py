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

worker_process_num = 3

# init logger
log_dir = ""
consumer_logger = None
# init db
dbutil = None

def handle_msg(msg):
	consumer_logger.debug(msg)
	try:
		msg_obj = json.loads(msg)
	except Exception as e:
		consumer_logger.error("unvalid json string: %s" % (e))
		return

	if not msg_obj.has_key("organization"):
		consumer_logger.error("absence of 'organization'")
		return
	organization = msg_obj["organization"]

	if not msg_obj.has_key("service"):
		consumer_logger.error("absence of 'service'")
		return
	service = msg_obj["service"]

	if not msg_obj.has_key("method"):
		consumer_logger.error("absence of 'method'")
		return
	method = msg_obj["method"]

	if msg_obj.has_key("timestamp"):
		invoked_time = msg_obj["timestamp"] # unix time, int
	else:
		invoked_time = int(time.time())

	if not msg_obj.has_key("error_code"):
		consumer_logger.error("absence of 'error_code'")
		return
	return_code = int(msg_obj["error_code"])

	if not msg_obj.has_key("project"):
		consumer_logger.error("absence of 'project'")
		return
	project = msg_obj["project"]

	request = ""
	if msg_obj.has_key("request"):
		request = msg_obj["request"]
	response = ""
	if msg_obj.has_key("response"):
		response = msg_obj["response"]
	
	# save the data into database
	if return_code == 0:
		cur_day = datetime.date.today()
		start_time = time_util.unix_time(str(cur_day) + ' 00:00:00')
		sql = "insert into api_logs(organization, service, method, invoked_time, return_code, request, response, project) values(\"%s\", \"%s\", \"%s\", %d, %d, \"%s\", \"%s\", \"%s\") on duplicate key update frequency = frequency + 1" % (organization, service, method, start_time, return_code, MySQLdb.escape_string(request), MySQLdb.escape_string(response), project)
	else:
		sql = "insert into api_logs(organization, service, method, invoked_time, return_code, request, response, project) values(\"%s\", \"%s\", \"%s\", %d, %d, \"%s\", \"%s\", \"%s\") on duplicate key update frequency = frequency + 1" % (organization, service, method, invoked_time, return_code, MySQLdb.escape_string(request), MySQLdb.escape_string(response), project)
	consumer_logger.debug(sql)
	dbutil.execute(sql)


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
	logger_name = "logstat.consumer"
	logger_file = log_dir + "/consumer.log"
	consumer_logger = logger.Logger(logger_name, logger_file, logging.DEBUG) # 线程安全

	dbutil = db_util.DBUtil(dbhost, dbport, dbname, dbuser, dbpasswd) # 线程安全
	
	client = KafkaClient(hosts=kafka_hosts)
	print "connect to kafka cluster"
	topic = client.topics[bytes(topic_name)]
	balanced_consumer = topic.get_balanced_consumer(
			consumer_group = "api_monitor_group",
			auto_commit_enable = True,
			zookeeper_connect = zk_hosts,
			num_consumer_fetchers = 2
		)
	print "consumer has been ready to consume message from topic '%s'" % (topic_name)

	pool = multiprocessing.Pool(processes=worker_process_num)
	for msg in balanced_consumer:
		if msg is not None:
			pool.apply_async(handle_msg, (msg.value, )) # 跨进程传递的参数需要能够串行化pickled
	
	pool.close()
	del dbutil
	pool.join()

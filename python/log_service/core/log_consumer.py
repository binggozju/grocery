#!/usr/bin/python
#coding=utf-8
"""
consume the log of every api call from kafka, then store them into mysql.
"""

import json
import multiprocessing
import time
import MySQLdb

from log_service.common import kafka
from log_service.common import dbutil
from log_service.common import logger
from log_service.common import timeutil


topic = ""
consumer_group = ""

consumer_num = 3    # the number of consumers (process)

consumer_logger = None  # thread-safe
db_util = None  # thread-safe

def init(topic_name, consumer_group_name):
    global topic, consumer_group
    topic = topic_name
    consumer_group = consumer_group_name

    global consumer_logger, db_util
    consumer_logger = logger.get_logger("root.log_consumer")
    db_util = dbutil.DBUtil()
    print "init the log_consumer module successfully"


def _handle_msg(msg):
    """
    parse the log message, and store them
    """
    try:
        json_msg = json.loads(msg)
    except Exception as e:
        consumer_logger.error("invalid json string: %s" % (e))
        return
    
    # parse the log message
    if not json_msg.has_key("organization"):
        consumer_logger.error("absence of 'organization'")
        return
    organization = json_msg["organization"]

    if not json_msg.has_key("service"):
        consumer_logger.error("absence of 'service'")
        return
    service = json_msg["service"]

    if not json_msg.has_key("method"):
        consumer_logger.error("absence of 'method'")
        return
    method = json_msg["method"]

    invoked_time = int(time.time()) # unix time
    if json_msg.has_key("timestamp"):
        invoked_time = json_msg["timestamp"]

    if not json_msg.has_key("error_code"):
        consumer_logger.error("absence of 'error_code'")
        return
    return_code = int(json_msg["error_code"])

    if not json_msg.has_key("project"):
        consumer_logger.error("absence of 'project'")
        return
    project = json_msg["project"]

    request = ""
    if json_msg.has_key("request"):
        request = json_msg["request"]

    response = ""
    if json_msg.has_key("response"):
        response = json_msg["response"]

    # store the log message
    if return_code == 0:
        # reset invoked_time
        today = timeutil.get_current_day()
        invoked_time = timeutil.to_unix_time(today + " 00:00:00")
    
    sql = "insert into api_logs(organization, service, method, invoked_time, return_code, request, response, project) values(\"%s\", \"%s\", \"%s\", %d, %d, \"%s\", \"%s\", \"%s\") on duplicate key update frequency = frequency + 1" % (organization, service, method, invoked_time, return_code, MySQLdb.escape_string(request), MySQLdb.escape_string(response), project)
    consumer_logger.debug("sql: %s" % (sql))
    db_util.execute(sql)


def start():
    """
    start the log_consumer
    """
    if consumer_logger == None:
        print "log_consumer has not been inited"
        return

    consumer_logger.info("create a consumer")
    consumer = kafka.get_consumer(topic, consumer_group) 

    consumer_logger.info("start to consume log from topic '%s'" % (topic))
    process_pool = multiprocessing.Pool(processes=consumer_num)
    for msg in consumer:
        if msg is not None:
            # 跨进程传递的参数需要能被串行化 (pickled)
            consumer_logger.debug("receive a log: %s" % (msg.value))
            process_pool.apply_async(_handle_msg, (msg.value, ))
    
    process_pool.close()
    process_pool.join()


if __name__ == "__main__":
    pass


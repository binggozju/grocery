#!/usr/bin/python
#coding=utf-8
"""
the entrance for consuming logs
"""

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
homepath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(homepath)
sys.path.append("/var/www")

from log_service.config import app_conf
from log_service.config import account_conf

from log_service.common import logger
from log_service.common import dbutil
from log_service.common import kafka

from log_service.core import log_consumer

# global configuration for log consumer
app_settings = None
account_settings = None

main_logger = None

def initialize(env):
    global app_settings, account_settings
    # load the config info
    app_settings = app_conf.get_app_settings(env)
    account_settings = account_conf.get_account_settings(env)
    print "load the config info successfully"

    # init the common utility
    logger.init(app_settings["log"]["log_consumer_app"]["home"], app_settings["log"]["log_consumer_app"]["file"])
    dbutil.init(account_settings["database"]["host"], account_settings["database"]["db"], account_settings["database"]["user"], account_settings["database"]["password"])
    kafka.init(app_settings["kafka_hosts"], app_settings["zk_hosts"])

    # init the log consumer module
    log_consumer.init(app_settings["api_log_consumer"]["topic"], app_settings["api_log_consumer"]["consumer_group"])

    global main_logger
    main_logger = logger.get_logger("root")
    if main_logger == None:
        print "fail to get the main logger"
        return

def main(argv):
    if len(argv) != 2:
        print "Usage: %s dev|production" % (argv[0])
        return
    if argv[1] not in ["dev", "production"]:
        print "Error: invalid parameter"
        print "Usage: %s dev|production" % (argv[0])
        return

    initialize(argv[1])
    if main_logger == None:
        print "fail to initialize the log consumer app"
        return

    main_logger.info("log consumer app has been started successfully")

    # start to consume the log from kafka
    log_consumer.start()


if __name__ == "__main__":
    sys.exit(main(sys.argv))

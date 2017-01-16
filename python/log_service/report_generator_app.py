#!/usr/bin/python
#coding=utf-8
"""
the entrance for generating daily report
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
from log_service.common import mailutil

from log_service.core import report_generator

# global configuration for report generator
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
    logger.init(app_settings["log"]["report_generator_app"]["home"], app_settings["log"]["report_generator_app"]["file"])
    dbutil.init(account_settings["database"]["host"], account_settings["database"]["db"], account_settings["database"]["user"], account_settings["database"]["password"])
    mailutil.init(account_settings["email"]["sender"], account_settings["email"]["password"])

    # init the report generator module
    report_generator.init(app_settings["report"]["daily_report_dir"], app_settings["report"]["error_log_dir"], app_settings["report_receivers"])

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
        print "fail to initialize the report generator app"
        return

    main_logger.info("report generator app has been started successfully")

    # start to generate daily report
    report_generator.start()


if __name__ == "__main__":
    sys.exit(main(sys.argv))

#!/usr/bin/python
#encoding=utf-8

import logging
import logging.handlers

class Logger():
	"""logger utility"""
	def __init__(self, logger_name, file_name, log_level=logging.DEBUG):
		formatter = logging.Formatter('%(asctime)-15s [%(levelname)s] %(message)s')
		handler = logging.handlers.RotatingFileHandler(file_name, maxBytes=100*1024*1024, backupCount=5)
		handler.setFormatter(formatter)
		
		self.logger = logging.getLogger(logger_name)
		self.logger.setLevel(log_level)
		self.logger.addHandler(handler)

	def debug(self, msg):
		self.logger.debug(msg)

	def info(self, msg):
		self.logger.info(msg)

	def warning(self, msg):
		self.logger.warning(msg)

	def error(self,msg):
		self.logger.error(msg)

if __name__ == "__main__":
	test_logger = Logger("logstat.test", "../logs/test.log", logging.INFO)
	test_logger.debug("this is a debug log")
	test_logger.info("this is a info log")
	test_logger.warning("this is a warn log")

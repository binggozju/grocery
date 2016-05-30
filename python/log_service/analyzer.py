#!/usr/bin/python
#encoding=utf-8

import sys 
reload(sys) 
sys.setdefaultencoding('utf8')
import os
import logging
import json
import datetime

from utils import logger
from utils import email_util
from utils import db_util
from utils import time_util


# configuration for db
dbhost = ""
dbport = 3306
dbname = ""
dbuser = ""
dbpasswd = ""

# init for email
sender = ""
passwd = ""
receiver = ""
mail_title = '统计日报'

# initialization for logging
log_dir = ""
analyzer_logger = None

# initialization for the report generated automatically
report_dir = './report_archive'
error_dir = './error_archive'
stat_report_file = report_dir + '/stat_report'

def send_mail(file_name, error_files):
	email_util.send_email(mail_title, file_name, error_files, receiver, sender, passwd)
	analyzer_logger.info("send email of stat report successfully")

def gen_success_rate(total, success):
	if 0 == total:
		success_rate = "100.00%"
	else:
		success_rate = "%.2f%%" % (float(success*100)/float(total))
	return success_rate

def analyze(start_time, end_time):
	"""
	- format of 'overview':
	{
		"organization1": {
			"service1": {
				"method1": {
					"project1": (total1, success1, failure1, success_rate1),
					"project2": (total2, success2, failure2, success_rate2)
				},
				"method2": {}
			},
			"service2": {...}
		},
		"organization2": {...}
	}

	--------------------------------------------------------------------
	- format of 'details':
	{
		"organization1": [
			("2016-05-10 12:00:00", "service1", "method1", "project1", 110, "request", "response")
			("2016-05-10 12:00:01", "service2", "method2", "project2",   0, "request", "response")
		],
		"organization2": [...]
	}
	"""
	overview = {}
	details = {}
	
	# initialization for db
	analyzer_logger.info("configuration for db: host -> %s, port -> %d, db -> %s" % (dbhost, dbport, dbname))
	dbutil = db_util.DBUtil(dbhost, dbport, dbname, dbuser, dbpasswd)

	sql_orgs = "select distinct organization from api_logs where invoked_time >= %d and invoked_time <= %d" % (start_time, end_time)
	analyzer_logger.debug(sql_orgs)
	orgs = dbutil.query(sql_orgs)
	for org in orgs:
		analyzer_logger.debug("analyze all services of organization '%s'" % (org[0]))
		# get overview
		org_info_map = {}

		sql_services = "select distinct service from api_logs where organization = '%s' and (invoked_time >= %d and invoked_time <= %d)" % (org[0], start_time, end_time)
		analyzer_logger.debug(sql_services)
		services = dbutil.query(sql_services)
		for service in services:
			analyzer_logger.debug("analyze all methods of service '%s'" % (service[0]))
			service_info_map = {}

			sql_methods = "select distinct method from api_logs where organization = '%s' and service = '%s' and (invoked_time >= %d and invoked_time <= %d)" % (org[0], service[0], start_time, end_time)
			analyzer_logger.debug(sql_methods)
			methods = dbutil.query(sql_methods)
			for method in methods:
				analyzer_logger.debug("analyze all projects of method '%s'" % (method[0]))
				method_info_map = {}

				sql_projects = "select distinct project from api_logs where organization = '%s' and service = '%s' and method = '%s' and (invoked_time >= %d and invoked_time <= %d)" % (org[0], service[0], method[0], start_time, end_time)
				analyzer_logger.debug(sql_projects)
				projects = dbutil.query(sql_projects)
				for p in projects:
					analyzer_logger.debug("analyze project '%s'" % (p[0]))
					# get total
					sql_total = "select sum(frequency) from api_logs where organization = '%s' and service = '%s' and method = '%s' and project = '%s' and (invoked_time >= %d and invoked_time <= %d)" % (org[0], service[0], method[0], p[0], start_time, end_time)
					analyzer_logger.debug(sql_total)
					dataset = dbutil.query(sql_total)
					if dataset[0][0] == None:
						total = 0
					else:
						total = dataset[0][0]
					# get success
					sql_success = "select sum(frequency) from api_logs where organization = '%s' and service = '%s' and method = '%s' and project = '%s' and return_code = 0 and (invoked_time >= %d and invoked_time <= %d)" % (org[0], service[0], method[0], p[0], start_time, end_time)
					analyzer_logger.debug(sql_success)
					dataset = dbutil.query(sql_success)
					if dataset[0][0] == None:
						success = 0
					else:
						success = dataset[0][0]
					
					analyzer_logger.debug("%s|%s|%s|%s statistical info: total -> %d, success -> %d" % (org[0], service[0], method[0], p[0], total, success))
					failure = total - success
					success_rate = gen_success_rate(total, success)
					method_info_map[p[0]] = (total, success, failure, success_rate)
					
				service_info_map[method[0]] = method_info_map
				
			org_info_map[service[0]] = service_info_map
			
		overview[org[0]] = org_info_map

		# get details (error log)
		errorlog_list = []
		sql_error_logs = "select invoked_time, service, method, project, return_code, request, response from api_logs where organization = '%s' and return_code != 0 and (invoked_time >= %d and invoked_time <= %d) order by invoked_time asc" % (org[0], start_time, end_time)
		error_logs = dbutil.query(sql_error_logs)

		for item in error_logs:
			log_info = tuple(item)
			errorlog_list.append(log_info)

		details[org[0]] = errorlog_list

	del dbutil
	result = (overview, details)
	return result

def generate_report(overview, details, report_file, error_files):
	# write report_file
	fd_report = open(report_file, 'w')
	fd_report.write("<h1 style=\"text-align:center;\"><span style=\"line-height:1.5;\">WMS接口调用统计报告</span></h1>\n")
	for org, org_info in overview.items():
		total, success = 0, 0
		for service, service_info in org_info.items():
			for method, method_info in service_info.items():
				for project, project_info in method_info.items():
					total += project_info[0]
					success += project_info[1]
	
		failure = total - success	
		success_rate = gen_success_rate(total, success)
		
		fd_report.write("<p>\n<table style=\"width:100%;background-color:#CCCCCC;\" cellpadding=\"2\" cellspacing=\"0\" border=\"2\" bordercolor=\"#000000\">\n<tbody>\n")
		fd_report.write("<tr>\n\
				<td style=\"text-align:center;\"><strong><span style=\"font-family:Microsoft YaHei;\">Organization</span></strong></td>\n\
				<td style=\"text-align:center;\"><strong><span style=\"font-family:Microsoft YaHei;\">Service</span></strong></td>\n\
				<td style=\"text-align:center;\"><strong><span style=\"font-family:Microsoft YaHei;\">Method</span></strong></td>\n\
				<td style=\"text-align:center;\"><strong><span style=\"font-family:Microsoft YaHei;\">Project</span></strong></td>\n\
				<td style=\"text-align:center;\"><strong><span style=\"font-family:Microsoft YaHei;\">Total</span></strong></td>\n\
				<td style=\"text-align:center;\"><strong><span style=\"font-family:Microsoft YaHei;\">Success</span></strong></td>\n\
				<td style=\"text-align:center;\"><strong><span style=\"font-family:Microsoft YaHei;\">Failure</span></strong></td>\n\
				<td style=\"text-align:center;\"><strong><span style=\"font-family:Microsoft YaHei;\">Success Rate</span></strong></td>\n\
				</tr>\n")
		for service, service_info in org_info.items():
			for method, method_info in service_info.items():
				for project, project_info in method_info.items():
					fd_report.write("<tr>\n\
							<td style=\"text-align:center;\">%s</td>\n\
							<td style=\"text-align:center;\">%s</td>\n\
							<td style=\"text-align:center;\">%s</td>\n\
							<td style=\"text-align:center;\">%s</td>\n\
							<td style=\"text-align:center;\">%d</td>\n\
							<td style=\"text-align:center;\">%d</td>\n\
							<td style=\"text-align:center;\">%d</td>\n\
							<td style=\"text-align:center;\">%s</td>\n\
							</tr>\n" % (org, service, method, project, project_info[0], project_info[1], project_info[2], project_info[3]))
		
		fd_report.write("<tr>\n<td style=\"text-align:center;\">%s</td>\n<td style=\"text-align:center;\">%s</td>\n<td style=\"text-align:center;\">%s</td>\n<td style=\"text-align:center;\">%s</td>\n<td style=\"text-align:center;\">%s</td>\n<td style=\"text-align:center;\">%d</td>\n<td style=\"text-align:center;\">%d</td>\n<td style=\"text-align:center;\">%s</td>\n</tr>\n" % ("合计", "", "", "", total, success, failure, success_rate))
		fd_report.write("</tbody>\n</table>\n</p>\n<hr />\n\n")

	fd_report.close()

	# write error_files
	for org, error_file in error_files.items():
		fd_error = open(error_file, 'w')
		fd_error.write("<!doctype html>\n<html>\n<meta charset=\"utf-8\"></meta>\n\
				<head>\n<script src=\"http://code.jquery.com/jquery-latest.js\"></script>\n\
				<script>\nfunction mouseDown($this){\n\
				if($this.parentElement.children[1].style.display  === \"none\"){\n\
				$this.parentElement.children[1].style.top  = $this.parentElement.offsetTop;\n\
				$this.parentElement.children[1].style.left = $this.parentElement.offsetLeft;\n\
				$this.parentElement.children[1].style.display='block';\n\
				}\nelse {\n\
					$this.parentElement.children[1].style.display='none';\n\
				}\n}\n</script>\n\
				<style type=\"text/css\">\n\
					.style-req-res{\n\
						display: none;\n\
						background-color: white;\n\
						border: 1px solid;\n\
						position: absolute;\n\
						}\n\
				</style>\n</head>\n<body>\n")

		fd_error.write("<p>\n\
				<table style=\"width:100%;background-color:#CCCCCC;\" cellpadding=\"2\" cellspacing=\"0\" border=\"2\" bordercolor=\"#000000\">\n\
				<tbody>\n<tr>\n\
				<td style=\"text-align:center;\"><strong>InvokedTime</strong></td>\n\
				<td style=\"text-align:center;\"><strong>Service</strong></td>\n\
				<td style=\"text-align:center;\"><strong>Method</strong></td>\n\
				<td style=\"text-align:center;\"><strong>Project</strong></td>\n\
				<td style=\"text-align:center;\"><strong>ReturnCode</strong></td>\n\
				<td style=\"text-align:center;\"><strong>Request</strong></td>\n\
				<td style=\"text-align:center;\"><strong>Response</strong></td>\n\
				</tr>\n\n")

		for log in details[org]:
			log_detail = (time_util.normal_time(log[0]), log[1], log[2], log[3], log[4], log[5][0:30]+" ...", log[5], log[6][0:30]+" ...", log[6])
			fd_error.write("<tr>\n\
					<td style=\"text-align:center;\">%s</td>\n\
					<td style=\"text-align:center;\">%s</td>\n\
					<td style=\"text-align:center;\">%s</td>\n\
					<td style=\"text-align:center;\">%s</td>\n\
					<td style=\"text-align:center;\">%d</td>\n\
					<td><label onmousedown=\"mouseDown(this)\"><script type=\"text/html\" style=\"display:block\">%s</script></label><div class=\"style-req-res\"><script type=\"text/html\" style=\"display:block\">%s</script></div></td>\n\
					<td><label onmousedown=\"mouseDown(this)\"><script type=\"text/html\" style=\"display:block\">%s</script></label><div class=\"style-req-res\"><script type=\"text/html\" style=\"display:block\">%s</script></div></td>\n\
					</tr>\n\n" % log_detail)

		fd_error.write("</tbody>\n</table>\n</p>\n</body>\n</html>\n")
		fd_error.close()


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
			dbhost = conf["pre-release"]["db"]["host"]
			dbport = conf["pre-release"]["db"]["port"]
			dbname = conf["pre-release"]["db"]["db_name"]
			dbuser = conf["pre-release"]["db"]["user"]
			dbpasswd = conf["pre-release"]["db"]["password"]
			sender = conf["pre-release"]["email"]["sender"] 
			passwd = conf["pre-release"]["email"]["password"]
			receiver = conf["pre-release"]["email"]["receiver"]
			log_dir = conf["pre-release"]["log"]["dir"]
	elif sys.argv[1] == "production":
		print "production"
		with open(config_file, 'r') as fd:
			conf = json.load(fd)
			dbhost = conf["production"]["db"]["host"]
			dbport = conf["production"]["db"]["port"]
			dbname = conf["production"]["db"]["db_name"]
			dbuser = conf["production"]["db"]["user"]
			dbpasswd = conf["production"]["db"]["password"]
			sender = conf["production"]["email"]["sender"] 
			passwd = conf["production"]["email"]["password"]
			receiver = conf["production"]["email"]["receiver"]
			log_dir = conf["production"]["log"]["dir"]
	else:
		print "invalid parameter"
		sys.exit()
	
	if os.path.exists(log_dir) == False:
		print "log dir '%s' not exist" % (log_dir)
		sys.exit()
	logger_name = "logstat.analyzer"
	logger_file = log_dir + "/analyzer.log"
	analyzer_logger = logger.Logger(logger_name, logger_file, logging.DEBUG)
	
	analyzer_logger.info("start to analyze...")
	if os.path.exists(report_dir) == False:
		os.mkdir(report_dir)
		analyzer_logger.info("make the directory " + report_dir)
	if os.path.exists(error_dir) == False:
		os.mkdir(error_dir)
		analyzer_logger.info("make the directory " + error_dir)
	
	# initialization
	this_day = datetime.date.today()
	stat_report_file = stat_report_file + "_" + this_day.strftime("%Y%m%d") + ".html"
	analyzer_logger.debug("stat_report_file: " + stat_report_file)
	
	error_dir = error_dir + "/" + this_day.strftime("%Y%m%d")
	if os.path.exists(error_dir) == False:
		os.mkdir(error_dir)

	mail_title = "[" + this_day.strftime("%Y-%m-%d") + "]" + mail_title

	# analyze data from db
	yesterday = this_day - datetime.timedelta(days=1)
	start_time = time_util.unix_time(str(yesterday) + ' 00:00:00') 
	end_time = time_util.unix_time(str(yesterday) + ' 23:59:59')
	(overview, details) = analyze(start_time, end_time)

	# generate statistical report automatically
	error_files = {}
	for org in overview.keys():
		error_files[org] = error_dir + "/" + org + ".html"
	generate_report(overview, details, stat_report_file, error_files)

	send_mail(stat_report_file, error_files.values())
	analyzer_logger.info("complete today's statistical report")

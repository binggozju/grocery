#!/usr/bin/python
#coding=utf-8
"""
generate the daily report according to the data stored in mysql.
"""

import os
import datetime

from log_service.common import dbutil
from log_service.common import logger
from log_service.common import mailutil
from log_service.common import timeutil
from log_service.common import report


daily_report_dir = ""
daily_report_file = ""
daily_report_title = "WMS接口调用统计日报"
daily_report_receivers = ""

error_log_dir = ""

generator_logger = None
db_util = None

today = None

def init(report_dir, errorlog_dir, receivers):
    global daily_report_dir, error_log_dir, daily_report_receivers
    daily_report_dir = report_dir
    error_log_dir = errorlog_dir
    daily_report_receivers = receivers

    global generator_logger, db_util
    generator_logger = logger.get_logger("root.report_generator")
    db_util = dbutil.DBUtil()
   
    global today, daily_report_title, daily_report_file
    today = datetime.date.today()
    daily_report_title = "[%s] %s" % (today.strftime("%Y-%m-%d"), daily_report_title)
    daily_report_file = "%sdaily_report_%s.html" % (daily_report_dir, today.strftime("%Y%m%d"))

    # create directory for daily report
    if not os.path.exists(daily_report_dir):
        print "create directory: %s" % (daily_report_dir)
        os.makedirs(daily_report_dir)

    # create directory for error log
    error_log_dir += today.strftime("%Y%m%d") + "/"
    if not os.path.exists(error_log_dir):
        print "create directory: %s" % (error_log_dir)
        os.makedirs(error_log_dir)

    print "init the report_generator module successfully"


def _get_success_rate(total, success):
    if 0 == total:
        success_rate = "100.00%"
    else:
        success_rate = "%.2f%%" % (float(success*100)/float(total))
    return success_rate


def _analyze(start_time, end_time):
    """
    * overview的数据组织格式
    {
        "organization1": {
            "service1": {
                "method1": {
                    "project1": (total1, success1, failure1, success_rate1),
                    "project2": (total2, success2, failure2, success_rate2)
                }
                "method2": {}
            },
            "service2": {...}
        },
        "organization2": {...}
    }
    * -----------------------------------------------------------------------------
    * details的数组组织格式
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

    global db_util
    sql_orgs = "select distinct organization from api_logs where invoked_time >= %d and invoked_time <= %d" % (start_time, end_time)
    generator_logger.debug(sql_orgs)
    orgs = db_util.query(sql_orgs)
    for org in orgs:
        generator_logger.debug("analyze all services of organization '%s'" % (org[0]))
        # start to get data for overview
        org_info_map = {}

        sql_services = "select distinct service from api_logs where organization = '%s' and (invoked_time >= %d and invoked_time <= %d)" % (org[0], start_time, end_time)
        generator_logger.debug(sql_services)
        services = db_util.query(sql_services)
        for service in services:
            generator_logger.debug("analyze all methods of service '%s'" % (service[0]))
            service_info_map = {}

            sql_methods = "select distinct method from api_logs where organization = '%s' and service = '%s' and (invoked_time >= %d and invoked_time <= %d)" % (org[0], service[0], start_time, end_time)
            generator_logger.debug(sql_methods)
            methods = db_util.query(sql_methods)
            for method in methods:
                generator_logger.debug("analyze all projects of method '%s'" % (method[0]))
                method_info_map = {}

                sql_projects = "select distinct project from api_logs where organization = '%s' and service = '%s' and method = '%s' and (invoked_time >= %d and invoked_time <= %d)" % (org[0], service[0], method[0], start_time, end_time)
                generator_logger.debug(sql_projects)
                projects = db_util.query(sql_projects)
                for p in projects:
                    generator_logger.debug("analyze project '%s'" % (p[0]))
                    # get total num
                    sql_total = "select sum(frequency) from api_logs where organization = '%s' and service = '%s' and method = '%s' and project = '%s' and (invoked_time >= %d and invoked_time <= %d)" % (org[0], service[0], method[0], p[0], start_time, end_time)
                    generator_logger.debug(sql_total)
                    dataset = db_util.query(sql_total)
                    if dataset[0][0] == None:
                        total = 0
                    else:
                        total = dataset[0][0]

                    # get success num
                    sql_success = "select sum(frequency) from api_logs where organization = '%s' and service = '%s' and method = '%s' and project = '%s' and return_code = 0 and (invoked_time >= %d and invoked_time <= %d)" % (org[0], service[0], method[0], p[0], start_time, end_time)
                    generator_logger.debug(sql_success)
                    dataset = db_util.query(sql_success)
                    if dataset[0][0] == None:
                        success = 0
                    else:
                        success = dataset[0][0]

                    generator_logger.debug("%s|%s|%s|%s statistical info: total -> %d, success -> %d" % (org[0], service[0], method[0], p[0], total, success))
                    failure = total - success
                    success_rate = _get_success_rate(total, success)
                    method_info_map[p[0]] = (total, success, failure, success_rate)

                service_info_map[method[0]] = method_info_map

            org_info_map[service[0]] = service_info_map

        overview[org[0]] = org_info_map

        # start to get data for details (error log)
        error_log_list = []

        sql_error_logs = "select invoked_time, service, method, project, return_code, request, response from api_logs where organization = '%s' and return_code != 0 and (invoked_time >= %d and invoked_time <= %d) order by invoked_time asc" % (org[0], start_time, end_time)
        error_logs = db_util.query(sql_error_logs)
        for item in error_logs:
            log_info = tuple(item)
            error_log_list.append(log_info)

        details[org[0]] = error_log_list

    del db_util
    result = (overview, details)
    return result


def _generate_daily_report(overview):
    daily_report = report.DailyReport(daily_report_file, "WMS接口调用统计报告")
    daily_report.open()
    
    for org, org_info in overview.items():
        total, success = 0, 0
        for service, service_info in org_info.items():
            for method, method_info in service_info.items():
                for project, project_info in method_info.items():
                    total += project_info[0]
                    success += project_info[1]
        failure = total - success
        success_rate = _get_success_rate(total, success)

        table_header = ["Organization", "Service", "Method", "Project", "Total", "Success", "Failure", "Success Rate"]
        daily_report.write_table_header(table_header)
        
        for service, service_info in org_info.items():
            for method, method_info in service_info.items():
                for project, project_info in method_info.items():
                    row = [org, service, method, project, str(project_info[0]), str(project_info[1]), str(project_info[2]), project_info[3]]
                    daily_report.write_table_row(row)
        
        table_footer = ["合计", "", "", "", str(total), str(success), str(failure), success_rate]
        daily_report.write_table_footer(table_footer)
        generator_logger.debug("complete to write table for '%s'" % (org))

    daily_report.close()


def _generate_error_log_reports(details, error_files):
    for org, error_file in error_files.items():
        error_log_report = report.ErrorLogReport(error_file)
        error_log_report.open()

        table_header = ["InvokedTime", "Service", "Method", "Project", "ReturnCode", "Request", "Response"]
        error_log_report.write_table_header(table_header)

        for log in details[org]:
            log_detail = [timeutil.to_normal_time(log[0]), log[1], log[2], log[3], str(log[4]), log[5], log[6]]
            error_log_report.write_table_row(log_detail)

        error_log_report.write_table_footer([])
        error_log_report.close()


def start():
    """
    start the report_generator
    """
    if generator_logger == None:
        print "report_generator has not been inited"
        return
    
    # analyze the data of yesterday
    yesterday = today - datetime.timedelta(days=1)
    start_time = timeutil.to_unix_time(str(yesterday) + " 00:00:00")
    end_time = timeutil.to_unix_time(str(yesterday) + " 23:59:59")
    (overview, details) = _analyze(start_time, end_time)
    generator_logger.info("complete the analysis")

    # generate daily report
    _generate_daily_report(overview)
    generator_logger.info("complete to generate the daily report")

    # generate error log (report)
    error_log_files = {}
    for organization  in overview.keys():
        error_log_files[organization] = "%s%s-%s.html" % (error_log_dir, organization, today.strftime("%Y%m%d"))

    _generate_error_log_reports(details, error_log_files)
    generator_logger.info("complete to generate the error log reports")

    # send the reports
    with open(daily_report_file, "r") as fd:
        daily_report_content = fd.read()

    result = mailutil.send_email(daily_report_title, daily_report_content, [], daily_report_receivers)
    # result = mailutil.send_email(daily_report_title, daily_report_content, error_log_files.values(), daily_report_receivers)
    if result == 0:
        generator_logger.info("send the mail to %s successfully" % (daily_report_receivers))
    else:
        generator_logger.info("fail to send the mail")


if __name__ == "__main__":
    pass


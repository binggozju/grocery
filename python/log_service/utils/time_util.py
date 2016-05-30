#!/usr/bin/python
#encoding=utf-8
"""
utility function related with time and date
"""


import datetime
import time

def unix_time(str_normal_time):
	"""
	'%Y-%m-%d %H:%M:%S' -> unix time
	"""
	return int(time.mktime(time.strptime(str_normal_time, '%Y-%m-%d %H:%M:%S')))

def normal_time(int_unix_time):
	"""
	unix time -> '%Y-%m-%d %H:%M:%S'
	"""
	t = time.localtime(int(int_unix_time))
	format = '%Y-%m-%d %H:%M:%S'
	return time.strftime(format, t)


if __name__ == "__main__":
	yesterday = datetime.date.today()-datetime.timedelta(days=1)
	str_start_time = str(yesterday) + ' 00:00:00'
	str_end_time = str(yesterday) + ' 23:59:59'

	start_time = unix_time(str_start_time)
	print str_start_time, start_time
	end_time = unix_time(str_end_time)
	print str_end_time, end_time

	now_time = int(time.time())
	str_now_time = normal_time(now_time)
	print now_time, str_now_time

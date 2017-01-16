#!/usr/bin/python
"""
utility function related with time and date
"""

import datetime
import time

def get_current_day():
    """
    return the current day format '2016-08-03'
    """
    return time.strftime('%Y-%m-%d',time.localtime(time.time()))

def to_unix_time(normal_time):
    """
    '%Y-%m-%d %H:%M:%S' -> unix time
    """
    return int(time.mktime(time.strptime(normal_time, '%Y-%m-%d %H:%M:%S')))

def to_normal_time(unix_time):
    """
    unix time -> '%Y-%m-%d %H:%M:%S'
    """
    format = '%Y-%m-%d %H:%M:%S'
    return time.strftime(format, time.localtime(int(unix_time)))


if __name__ == "__main__":
    yesterday = datetime.date.today()-datetime.timedelta(days=1)
    normal_time = str(yesterday) + ' 10:10:10'
    print "normal time: %s" % (normal_time)

    unix_time = to_unix_time(normal_time)
    print "unix time: %s" % (unix_time)

    print "current day: %s" % (get_current_day())
    if "2016-08-25" != get_current_day():
        print "this day is not 2016-08-25"

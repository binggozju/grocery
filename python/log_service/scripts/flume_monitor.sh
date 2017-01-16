#!/bin/bash
#---------------------------------------------------------------
# Description: 每隔2分钟定期监控flume进程，当flume挂掉时，
#     自动拉起新的flume进程.
# Crontab: */2 * * * *  /root/log_service/monitors/flume_monitor.sh
#---------------------------------------------------------------


WORKING_DIR=$(dirname `readlink -m $0`)
cd $WORKING_DIR/..
LOG_FILE=/data0/log_service/flume_monitor.log

function log() {
	local log_level=$1
	local log_msg=$2
	local date_str=$(date +"%Y-%m-%d %H:%M:%S")
	echo "$date_str [$log_level] $log_msg" >> $LOG_FILE
}

EXIST_AGENT=$(ps aux | grep flume-conf.properties | grep -v grep | wc -l)
if [ $EXIST_AGENT -gt 0 ]; then
	log INFO "flume is running"
else
	log ERROR "flume has stopped"
	nohup /opt/apache-flume-1.6.0-bin/bin/flume-ng agent -c /opt/apache-flume-1.6.0-bin/conf -f /opt/apache-flume-1.6.0-bin/conf/flume-conf.properties -n agent &
	log INFO "flume monitor has restarted flume"
fi

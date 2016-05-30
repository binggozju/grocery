#!/bin/bash
#--------------------------------------------------------------------------
# Description: 每隔2分钟检测一次logstash进程，当logstash进程挂掉时自动拉起
# Crontab: */2 * * * *  /root/logstash-monitor.sh
#--------------------------------------------------------------------------

MONITOR_LOG_FILE=/data0/logs/logstash/monitor.log
LOGSTASH_LOG_FILE=/data0/logs/logstash/logstash.log

function log() {
	local log_level=$1
	local log_msg=$2
	local date_str=$(date +"%Y-%m-%d %H:%M:%S")
	echo "$date_str [$log_level] $log_msg" >> $MONITOR_LOG_FILE
}

EXIST_AGENT=$(ps aux | grep "logstash/runner.rb" | grep -v grep | wc -l)
if [ $EXIST_AGENT -gt 0 ]; then
	log INFO "logstash is running"
else
	log ERROR "logstash has stopped"
	nohup /opt/logstash/bin/logstash -f /opt/logstash/config/archiver.conf --auto-reload 2>&1 >> $LOGSTASH_LOG_FILE &
	log INFO "logstash-monitor has restarted logstash"
fi

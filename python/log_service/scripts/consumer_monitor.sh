#!/bin/bash
#---------------------------------------------------------------
# Description: 每隔5分钟定期监控consumer进程，当consumer挂掉时，
#     自动拉起新的consumer进程.
# Crontab: */5 * * * *  /var/www/log_service/scripts/consumer_monitor.sh
#---------------------------------------------------------------


WORKING_DIR=$(dirname `readlink -m $0`)
LOG_FILE=/data0/log_service/monitor/consumer_monitor.log

function log() {
	local log_level=$1
	local log_msg=$2
	local date_str=$(date +"%Y-%m-%d %H:%M:%S")
	echo "$date_str [$log_level] $log_msg" >> $LOG_FILE
}

EXIST_AGENT=$(ps aux | grep "log_consumer_app.py" | grep -v grep | wc -l)
if [ $EXIST_AGENT -gt 0 ]; then
	log INFO "log_consumer_app service is running"
else
	log ERROR "log_consumer_app service has stopped"
	cd $WORKING_DIR/..
	nohup python log_consumer_app.py production 2>&1 > /dev/null &
	log INFO "consumer monitor has restarted consumer"
	cd -
fi

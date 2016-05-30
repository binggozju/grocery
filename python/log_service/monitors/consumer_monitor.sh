#!/bin/bash
#---------------------------------------------------------------
# Description: 每隔2分钟定期监控consumer进程，当consumer挂掉时，
#     自动拉起新的consumer进程.
# Crontab: */2 * * * *  /root/log_stat/monitors/consumer_monitor.sh
#---------------------------------------------------------------

WORKING_DIR=$(dirname `readlink -m $0`)
cd $WORKING_DIR/..
LOG_FILE=./logs/consumer_monitor.log

function log() {
	local log_level=$1
	local log_msg=$2
	local date_str=$(date +"%Y-%m-%d %H:%M:%S")
	echo "$date_str [$log_level] $log_msg" >> $LOG_FILE
}

EXIST_AGENT=$(ps aux | grep "python consumer" | grep -v grep | wc -l)
if [ $EXIST_AGENT -gt 0 ]; then
	log INFO "kafka consumer is running"
else
	log ERROR "kafka consumer has stopped"
	nohup python consumer_v2.py > /dev/null 2>&1 &
	log INFO "consumer monitor has restarted kafka consumer"
fi

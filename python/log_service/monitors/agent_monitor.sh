#!/bin/bash
#---------------------------------------------------------------
# Description: 每隔2分钟定期监控flume agent进程，当agent挂掉时，
#     自动拉起新的agent进程.
# Crontab: */2 * * * *  /root/log_stat/monitors/agent_monitor.sh
#---------------------------------------------------------------


WORKING_DIR=$(dirname `readlink -m $0`)
cd $WORKING_DIR/..
LOG_FILE=./logs/agent_monitor.log

function log() {
	local log_level=$1
	local log_msg=$2
	local date_str=$(date +"%Y-%m-%d %H:%M:%S")
	echo "$date_str [$log_level] $log_msg" >> $LOG_FILE
}

EXIST_AGENT=$(ps aux | grep logagent.conf | grep -v grep | wc -l)
if [ $EXIST_AGENT -gt 0 ]; then
	log INFO "flume agent is running"
else
	log ERROR "flume agent has stopped"
	nohup /usr/local/flume/bin/flume-ng agent -c /usr/local/flume/conf -f /usr/local/flume/conf/logagent.conf -n http_agent > /dev/null 2>&1 &
	log INFO "agent monitor has restarted flume agent"
fi

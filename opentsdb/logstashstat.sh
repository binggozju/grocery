#!/bin/bash
# logstash stat for OpenTSDB

metric=logstash.host.mem
interval=10s	# 5s, 5m, 5h

while ((1)); do
	nowtime=$(date +%s)
	hostname=$(hostname)
	
	pid=$(ps aux | grep "logstash/runner.rb" | grep -v grep | awk -F " " '{print $2}')
	if [ -n "$pid" ]; then	# process exist
		mem=$(eval cat /proc/${pid}/stat | awk -F" " '{print $24}') # 1 page => 4KB
		mem=$[$mem * 4 / 1024] # MB
		echo "$metric $nowtime $mem host=${hostname}"
	else
		echo "$metric $nowtime 0 host=${hostname}"
	fi

	sleep $interval
done

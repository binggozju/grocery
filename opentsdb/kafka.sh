#!/bin/bash
# -----------------------------------------------------------------
# kafka statistics based on JMXTerm for OpenTSDB.
# modify METRICS and jmxterm_cmd() if you want to add new metric.
# -----------------------------------------------------------------

DIR=$(dirname `readlink -m $0`)
INTERVAL=60	# second
JMXTERM=$DIR/../lib/jmxterm-1.0-alpha-4-uber.jar
#JMXTERM=/var/www/tcollector/collector/lib/jmxterm-1.0-alpha-4-uber.jar

KAFKA_HOSTS=(iZ23eik4gkzZ iZ23jp9elh7Z iZ23491st0hZ)
KAFKA_JMXRMIS=(10.168.72.226:6140 10.168.76.90:6140 10.168.59.183:6140)
HOST_LENGTH=${#KAFKA_HOSTS[*]}

METRICS=(kafka.server.messagein kafka.server.bytesin kafka.server.byteout)
METRIC_LENGTH=${#METRICS[*]}

# get the value of mbean related with metrics above
function jmxterm_cmd() {
local rmi=$1
cat <<EOF
open $rmi
get -s -b kafka.server:name=MessagesInPerSec,type=BrokerTopicMetrics OneMinuteRate
get -s -b kafka.server:name=BytesInPerSec,type=BrokerTopicMetrics OneMinuteRate
get -s -b kafka.server:name=BytesOutPerSec,type=BrokerTopicMetrics OneMinuteRate
close
EOF
}

while ((1)); do
	now_time=$(date +%s)

	# deal with each kafka host
	for ((i=0; i<$HOST_LENGTH; i++)); do
		host=${KAFKA_HOSTS[$i]}
		jmxrmi=${KAFKA_JMXRMIS[$i]}

		result=$(eval jmxterm_cmd $jmxrmi | java -jar $JMXTERM -v silent -n)
		result_array=($result)
		
		# deal with each metric
		for ((j=0; j<$METRIC_LENGTH; j++)); do
			metric_name=${METRICS[$j]}
			metric_value=${result_array[$j]}

			echo "$metric_name $now_time $metric_value host=$host"
		done
	done

	sleep_time=$[$now_time + $INTERVAL - $(date +%s)]
	sleep ${sleep_time}s
done

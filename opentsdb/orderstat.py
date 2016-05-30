#!/usr/bin/python
"""order quantity statistics for OpenTSDB"""

import time
import sys
#import multiprocessing
import threading
import json
from pykafka import KafkaClient


interval = 20	# TODO period for sending data to TSDB, seconds

topic_name = "orders"
kafka_hosts = "127.0.0.1:9092,127.0.0.1:9093" # pre-release
#kafka_hosts = "10.168.72.226:9092,10.168.76.90:9092,10.168.59.183:9092" # product
zk_hosts = "127.0.0.1:2181" # pre-release
#zk_hosts = "10.168.72.226:2181,10.168.76.90:2181,10.168.59.183:2181" # product


metrics = {
		# metric:			  tag_name1,  tag_name2, ...
		"trading.orders.num": ["region", "goodstype"]
		}
metrics_data = {}


def initialize():
	"""
	metrics_data format: {
		"metric1": {
			"tag1-v1": {
				"tag2-v1": 100,
				"tag2-v2": 80
			},
			"tag1-v2": {...},
		},
		"metric2": {...}
	}
	"""
	global metrics, metrics_data
	for metric_name, tag_names in metrics.items():
		if len(tag_names) > 0:
			metrics_data[metric_name] = {}
		else:
			metrics_data[metric_name] = 0


def update_metric_data(msg, sync_event):
	"""attention: trading.orders.num default"""
	try:
		msg_obj = json.loads(msg)
	except Exception as e:
		return

	global metrics, metrics_data
	
	tag_values = []
	for tag_name in metrics["trading.orders.num"]:
		if tag_name not in msg_obj:
			return
		tag_values.append(msg_obj[tag_name])

	sync_event.wait() # if sync_event has not been set, then wait() will be blocked

	if len(metrics["trading.orders.num"]) == 0: # metric without any tag
		metrics_data["trading.orders.num"] += 1
		return

	dict_cursor = metrics_data["trading.orders.num"]
	for tag_value in tag_values[:-1]:
		if tag_value not in dict_cursor:
			dict_cursor[tag_value] = {}
		dict_cursor = dict_cursor[tag_value]
	
	if tag_values[-1] not in dict_cursor:
		dict_cursor[tag_values[-1]] = 1
	else:
		dict_cursor[tag_values[-1]] += 1


def test_update_metric_data():
	msg = {"region": "r1", "goodstype": "t1"}
	msg_str = json.dumps(msg)

	global metrics, metrics_data
	initialize()
	e = threading.Event()
	e.set()

	update_metric_data(msg_str, e)
	print metrics_data
	update_metric_data(msg_str, e)
	print metrics_data


def aggregate(sync_event):
	"""aggregate the order data from kafka for the given metrics"""
	global kafka_hosts, topic_name, zk_hosts
	kafka_client = KafkaClient(hosts=kafka_hosts)
	topic = kafka_client.topics[topic_name]
	balanced_consumer = topic.get_balanced_consumer(
				consumer_group = "orders_group",
				auto_commit_enable = True,
				zookeeper_connect = zk_hosts
			)

	for msg in balanced_consumer:
		if msg is not None:
			update_metric_data(msg.value, sync_event)


def print_recursively(metric_data_str, tag_values, data):
	if not isinstance(data, dict): # leaf node
		print metric_data_str % tuple([data] + tag_values)
		return

	for key, val in data.items():
		print_recursively(metric_data_str, tag_values + [key], val)


def send_data(sync_event):
	"""
	print metric data every ${interval} minutes, and tcollector will send them to TSDB automatically.
	"""
	global metrics, metrics_data
	global interval

	while True:
		sync_event.clear()
		data_sended = metrics_data
		metrics_data = {}
		initialize()
		sync_event.set()

		# print the data of every leaf node in data_sended
		timestamp = int(time.time())
		for metric_name, val in data_sended.items():
			# metric_data_str: metric_name timestamp metric_value tag1=tag1-1 tag2=tag2-1
			metric_data_str = metric_name + " " + str(timestamp) + " %d"
			for tag_name in metrics[metric_name]:
				metric_data_str = metric_data_str + " " + tag_name + "=%s"
		
			tag_values = []
			print_recursively(metric_data_str, tag_values, val)

		data_sended = None

		sleep_time = interval + timestamp - int(time.time())
		time.sleep(sleep_time)


def test_send_data():
	global metrics_data
	metrics_data = {
			"trading.orders.num": {
				"tag1-value1": { "tag2-value1": 10, "tag2-value2": 30 },
				},
			"trading.orders.test": 100
			}
	
	e = threading.Event()
	e.set()
	send_data(e)


def main():
	initialize()

	sync_event = threading.Event()
	sync_event.set()
	thread_aggregate = threading.Thread(name="aggregate_thread", target=aggregate, args=(sync_event,))
	thread_send_data = threading.Thread(name="send_data_thread", target=send_data, args=(sync_event,))
	
	thread_aggregate.start()
	thread_send_data.start()


if __name__ == "__main__":
	sys.exit(main())

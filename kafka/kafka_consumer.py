#!/usr/bin/python

from pykafka import KafkaClient

# configuration for kafka
topic_name = "orders"
#topic_name = "wmslog-test"
#kafka_hosts = "10.168.72.226:9092,10.168.76.90:9092,10.168.59.183:9092" # product
kafka_hosts = "127.0.0.1:9092,127.0.0.1:9093" # pre-release
#zk_hosts = "10.168.72.226:2181,10.168.76.90:2181,10.168.59.183:2181" # product
zk_hosts = "127.0.0.1:2181" # pre-release

def consume_msg(topic):
    print "start a balanced consumer"
    balanced_consumer = topic.get_balanced_consumer(
        consumer_group = "tools",
        auto_commit_enable = True,
		zookeeper_connect = zk_hosts)

    print "start to consume msg..."
    for msg in balanced_consumer:
        if msg is not None:
            print msg.offset, msg.value    


if __name__ == "__main__":
	client = KafkaClient(hosts=kafka_hosts)
	print "connect to kafka cluster"
	topic = client.topics[topic_name]
	consume_msg(topic)

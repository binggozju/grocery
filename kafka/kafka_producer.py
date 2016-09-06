#!/usr/bin/python

import sys
from pykafka import KafkaClient

topic_name = "test"

#kafka_hosts = "10.168.72.226:9092,10.168.76.90:9092,10.168.59.183:9092" # product
kafka_hosts = "127.0.0.1:9092,127.0.0.1:9093" # pre-release
#zk_hosts = "10.168.72.226:2181,10.168.76.90:2181,10.168.59.183:2181" # product
zk_hosts = "127.0.0.1:2181" # pre-release

def main():
    client = KafkaClient(hosts=kafka_hosts)
    topic = client.topics[topic_name]
    print "now you can send message to topic '%s'" % (topic_name)
    with topic.get_sync_producer() as producer:
        while True:
            msg = raw_input(">>> ")
            producer.produce(msg)
            print "send msg successfully"


if __name__ == "__main__":
    sys.exit(main())

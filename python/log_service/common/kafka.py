#!/usr/bin/python
"""
the kafka module based on pykafka
"""

from pykafka import KafkaClient

kafka_hosts = ""
zk_hosts = ""

def init(kafka, zk):
    global kafka_hosts, zk_hosts
    kafka_hosts = kafka
    zk_hosts = zk
    print "init the kafka module successfully"

def get_consumer(topic_name, consumer_group_name):
    client = KafkaClient(hosts=kafka_hosts)
    topic = client.topics[bytes(topic_name)]

    consumer = topic.get_balanced_consumer(
            consumer_group = consumer_group_name,
            auto_commit_enable = True,
            zookeeper_connect = zk_hosts,
            num_consumer_fetchers = 1
            )
    print "get a consumer of topic '%s'" % (topic_name)
    return consumer


if __name__ == "__main__":
    kafka_hosts = ""
    zk_hosts = ""
    consumer = get_consumer("xxx", "xxx")

    for msg in consumer:
        if msg is not None:
            print "receive a message from kafka: %s" % (msg.value)


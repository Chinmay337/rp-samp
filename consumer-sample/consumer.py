# consumer.py
from confluent_kafka import Consumer, KafkaError
import os

brokers = os.environ.get(
    "BROKERS", "redpanda.crud.svc.cluster.local:9093"
)  # Note the change in the domain

conf = {
    "bootstrap.servers": brokers,
    "group.id": "group1",
    "auto.offset.reset": "earliest",
    "security.protocol": "SSL",
    "ssl.ca.location": "./ca.crt",  # Adjusted path to the mounted certificate
}

# rest of your consumer code


c = Consumer(conf)
c.subscribe(["twitch_chat"])

while True:
    msg = c.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
    else:
        print("Received message: {}".format(msg.value().decode("utf-8")))

# producer.py
from confluent_kafka import Producer
import time
import os


def delivery_report(err, msg):
    if err is not None:
        print("Message delivery failed: {}".format(err))
    else:
        print("Message delivered to {} [{}]".format(msg.topic(), msg.partition()))


brokers = os.environ.get(
    "BROKERS", "redpanda.crud.svc.cluster.local:9093"
)  # Note the change in the domain

conf = {
    "bootstrap.servers": brokers,
    "security.protocol": "SSL",
    "ssl.ca.location": "./ca.crt",  # Adjusted path to the mounted certificate
    "ssl.endpoint.identification.algorithm": "none",  # Disable hostname verification
}

# rest of your producer code


p = Producer(conf)

for i in range(10):
    p.produce(
        "twitch_chat",
        key=str(i),
        value="message {}".format(i),
        callback=delivery_report,
    )
    time.sleep(1)

p.flush()

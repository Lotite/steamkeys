from confluent_kafka import Producer
import socket


def create_producer(server: str = "kafkalotfi.duckdns.org"):
    conf = {
        "bootstrap.servers": f"{server}:9092",
        "client.id": socket.gethostname(),
        "socket.timeout.ms": 5000,
        "message.timeout.ms": 5000,
    }
    return Producer(conf)

def sendMessage(producer:Producer, topic:str, key, value:str):
    producer.produce(topic, key=key, value=value)
    producer.flush()
        
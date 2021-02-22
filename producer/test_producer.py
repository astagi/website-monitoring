import os
import json
import pytest
import requests_mock
import time
import threading
from producer import Producer
from kafka import KafkaConsumer


default_config = [
    {"url": "https://developers.italia.it", "regexp": "data"},
]


@pytest.fixture
def create_json_config():
    config_file = "./config.json"
    f = open("./config.json", "w")
    f.write(json.dumps(default_config))
    f.close()
    yield None
    os.remove(config_file)


def test_producer_creates_objects(create_json_config, kafka_admin_client):

    kafka_admin_client.delete_topics(["reports"])
    producer = Producer()

    def launch_producer():
        producer.connect()
        with requests_mock.Mocker() as m:
            m.get('https://developers.italia.it', text='data')
            producer.start()

    launcher = threading.Thread(target=launch_producer)
    launcher.start()

    time.sleep(5)
    consumer = KafkaConsumer(
        "reports",
        bootstrap_servers=[f"{os.getenv('KAFKA_HOST', 'localhost:29092')}"],
        api_version=(0, 10),
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        consumer_timeout_ms=5000,
    )
    producer.stop()
    for msg in consumer:
        site_stat = json.loads(msg.value)
        assert msg.key.decode("utf-8") == "https://developers.italia.it"
        assert site_stat["status_code"] == 200
        assert site_stat["content_check"] is True
        assert site_stat["time"] > 0
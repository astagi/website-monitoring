import os
import time
import datetime
import json
import threading

from consumer import Consumer
from kafka import KafkaProducer


def test_consumer_receives_objects(kafka_admin_client, postgres_client):

    (db, db_cur) = postgres_client
    db_cur.execute("DROP TABLE IF EXISTS website_status;")
    db.commit()

    kafka_admin_client.delete_topics(["reports"])

    consumer = Consumer()

    producer = KafkaProducer(
        bootstrap_servers=[f"{os.getenv('KAFKA_HOST', 'localhost:29092')}"],
        api_version=(0, 10),
    )

    def launch_consumer():
        consumer.connect()
        consumer.start()

    launcher = threading.Thread(target=launch_consumer)
    launcher.start()

    time.sleep(3)

    url = "https://www.qwe.com"
    body_bytes = bytes(
        json.dumps(
            {
                "url": url,
                "status_code": 200,
                "content_check": True,
                "time": 2.56,
                "report_time": datetime.datetime.now().isoformat(),
            }
        ),
        encoding="utf-8",
    )
    producer.send("reports", key=bytes(url, encoding="utf-8"), value=body_bytes)
    producer.flush()
    time.sleep(5)
    consumer.stop()

    db_cur.execute("SELECT * from website_status;")
    records = db_cur.fetchall()

    assert len(records) == 1

    for row in records:
        assert row[1] == "https://www.qwe.com"
        assert row[2] == 200
        assert row[3] > 0

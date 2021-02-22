import os
import json
import re
import requests
import time
import datetime
from kafka import KafkaProducer


class Producer:
    def __init__(self):
        self._run = False

    def _send_report(self, url, content_check, status_code, time):
        url_bytes = bytes(url, encoding="utf-8")
        body_bytes = bytes(
            json.dumps(
                {
                    "url": url,
                    "status_code": status_code,
                    "content_check": content_check,
                    "time": time,
                    "report_time": datetime.datetime.now().isoformat(),
                }
            ),
            encoding="utf-8",
        )
        self._producer_instance.send("reports", key=url_bytes, value=body_bytes)

    def connect(self):
        self._producer_instance = None
        self._producer_instance = KafkaProducer(
            bootstrap_servers=[f"{os.getenv('KAFKA_HOST', 'localhost:29092')}"],
            api_version=(0, 10),
        )

    def start(self):
        config = []
        with open("./config.json", "r") as f:
            config = json.loads(f.read())
        self._run = True
        while self._run:
            for website in config:
                start = time.time()
                response = requests.get(website["url"])
                end = time.time()
                searched_content_ok = True
                if response.content and "regexp" in website:
                    x = re.search(website["regexp"], str(response.content))
                    searched_content_ok = x is not None
                self._send_report(
                    website["url"],
                    searched_content_ok,
                    response.status_code,
                    end - start,
                )
            time.sleep(2)

    def stop(self):
        self._run = False

import os
import json
import requests
import time

import datetime
from kafka import KafkaProducer


class Producer:

    def _send_report(self, url, content_check, status_code, time):
        print (url)
        print (status_code)
        print (time)
        try:
            url_bytes = bytes(url, encoding='utf-8')
            body_bytes = bytes(json.dumps({
                "url": url,
                "status_code": status_code,
                "content_check": content_check,
                "time": time,
                "report_time": datetime.datetime.now().isoformat()
            }), encoding='utf-8')
            self._producer_instance.send('report', key=url_bytes, value=body_bytes)
            self._producer_instance.flush()
            print('Message published successfully.')
        except Exception as ex:
            print('Exception in publishing message')
            print(str(ex))


    def connect(self):
        self._producer_instance = None
        try:
            self._producer_instance = KafkaProducer(
                bootstrap_servers=[f"{os.getenv('KAFKA_HOST', 'localhost')}:9092"],
                api_version=(0, 10)
            )
        except Exception as ex:
            print('Exception while connecting Kafka')
            print(str(ex))


    def start(self):
        config = []
        with open('./config.json', 'r') as f:
            config = json.loads(f.read())
        while True:
            for website in config:
                start = time.time()
                r = requests.get(website["url"])
                end = time.time()
                self._send_report(website["url"], True, r.status_code, end - start)
            time.sleep(2)

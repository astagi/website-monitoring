import json
import os
import psycopg2
from kafka import KafkaConsumer


class Consumer:

    def connect(self):
        self._db = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            dbname=os.getenv('POSTGRES_DB', 'postgres'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'postgres')
        )
        self._db_cur = self._db.cursor()
        self._db_cur.execute("DROP TABLE website_status;")
        self._db.commit()
        self._db_cur.execute("""
            CREATE TABLE website_status (id serial PRIMARY KEY, url varchar unique, status_code integer, content_check boolean, time decimal, report_time timestamp);
        """)
        self._db.commit()
        self._consumer = None
        try:
            self._consumer = KafkaConsumer(
                'report',
                auto_offset_reset='earliest',
                bootstrap_servers=[f"{os.getenv('KAFKA_HOST', 'localhost')}:9092"],
                api_version=(0, 10),
            )
        except Exception as ex:
            print('Exception while connecting Kafka')
            print(str(ex))

    def start(self):
        for msg in self._consumer:
            site_stat = json.loads(msg.value)
            print (msg.value)
            self._db_cur.execute("""
                INSERT INTO website_status (url, status_code, content_check, time, report_time)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT ON CONSTRAINT website_status_url_key
                DO UPDATE SET status_code=excluded.status_code, content_check=excluded.content_check, time=excluded.time, report_time=excluded.report_time;
            """,
            (msg.key.decode('utf-8'), site_stat["status_code"], site_stat["content_check"], site_stat["time"], site_stat["report_time"]))
            self._db.commit()
        self._consumer.close()
        self._db_cur.close()
        self._db.close()

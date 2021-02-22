import json
import os
import psycopg2
from kafka import KafkaConsumer


class Consumer:
    def __init__(self):
        self._run = False

    def connect(self):
        self._db = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            dbname=os.getenv("POSTGRES_DB", "postgres"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        )
        self._db_cur = self._db.cursor()
        self._db_cur.execute("DROP TABLE IF EXISTS website_status;")
        self._db.commit()
        self._db_cur.execute(
            """
        CREATE TABLE IF NOT EXISTS website_status (id serial PRIMARY KEY, url varchar unique, status_code integer, content_check boolean, time decimal, report_time timestamp);
        """
        )
        self._db.commit()
        self._consumer = None
        self._consumer = KafkaConsumer(
            "reports",
            group_id="group1",
            enable_auto_commit=False,
            consumer_timeout_ms=5000,
            bootstrap_servers=[f"{os.getenv('KAFKA_HOST', 'localhost:29092')}"],
            auto_offset_reset="earliest",
            api_version=(0, 10),
        )

    def start(self):
        self._run = True
        while self._run:
            for msg in self._consumer:
                site_stat = json.loads(msg.value)
                self._db_cur.execute(
                    """
                    INSERT INTO website_status (url, status_code, content_check, time, report_time)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT ON CONSTRAINT website_status_url_key
                    DO UPDATE SET status_code=excluded.status_code, content_check=excluded.content_check, time=excluded.time, report_time=excluded.report_time;
                """,
                    (
                        msg.key.decode("utf-8"),
                        site_stat["status_code"],
                        site_stat["content_check"],
                        site_stat["time"],
                        site_stat["report_time"],
                    ),
                )
                self._db.commit()
                self._consumer.commit()

    def stop(self):
        self._run = False
        self._db_cur.close()
        self._db.close()
        self._consumer.close()

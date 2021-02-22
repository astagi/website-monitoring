import os
import pytest
import psycopg2
from kafka import KafkaProducer, KafkaAdminClient


@pytest.fixture
def postgres_client():
    db = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        dbname=os.getenv("POSTGRES_DB", "postgres"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )
    db_cur = db.cursor()
    yield (db, db_cur)
    db_cur.close()
    db.close()


@pytest.fixture
def kafka_admin_client():
    kc = KafkaAdminClient(
        bootstrap_servers=[f"{os.getenv('KAFKA_HOST', 'localhost:29092')}"]
    )
    yield kc
    kc.close()

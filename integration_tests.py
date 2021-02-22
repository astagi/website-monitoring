import datetime
import os
import psycopg2
import time

# Wait for connections
db = None

while not db:
    try:
        db = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            dbname=os.getenv("POSTGRES_DB", "postgres"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        )
        db_cur = db.cursor()
    except Exception as ex:
        print (ex)

db_cur.execute(
    """
CREATE TABLE IF NOT EXISTS  website_status (id serial PRIMARY KEY, url varchar unique, status_code integer, content_check boolean, time decimal, report_time timestamp);
"""
)
db.commit()
db_cur.execute("DELETE FROM website_status;")
db.commit()

# Check databases for Oruga, Buefy and Developers Italia statuses

first_records = []
while not len(first_records) == 3:
    db_cur.execute("SELECT * from website_status;")
    records = db_cur.fetchall()
    for row in records:
        first_records.append(row)
        assert row[2] >= 200
        assert row[3] is True
        assert row[4] > 0
        assert row[5] < datetime.datetime.now()

# Check that data changes

changed = False

while not changed:
    db_cur.execute("SELECT * from website_status;")
    records = db_cur.fetchall()
    for (i, row) in enumerate(records):
        changed |= row[4] != first_records[i][4]
        changed |= row[5] < first_records[i][5]

# Close after some time
db_cur.close()
db.close()

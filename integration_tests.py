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

while True:
    try:
        db_cur.execute("DELETE FROM website_status;")
        db.commit()
        break
    except psycopg2.errors.UndefinedTable:
        pass

# Check databases for Oruga, Buefy and Developers Italia statuses
print ("Checking websites metrics are stored..")
first_records = []
while not len(first_records) == 3:
    db_cur.execute("SELECT * from website_status;")
    records = db_cur.fetchall()
    first_records = []
    for row in records:
        first_records.append(row)
        assert row[2] >= 200
        assert row[3] is True
        assert row[4] > 0
        assert row[5] < datetime.datetime.now()

# Check that data changes
print ("Checking websites metrics are changed..")
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

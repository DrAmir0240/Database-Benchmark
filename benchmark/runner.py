"""
Benchmark Runner
- Runs 8 queries on MongoDB and PostgreSQL
- 1000 iterations each
- Reports avg, p95, max latency
"""
import os
import time
import statistics
import json
from bson import ObjectId
from pymongo import MongoClient
import psycopg
from nanoid import generate
import uuid

from queries import *

RUNS = 1000


def bench(fn):
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        fn()
        times.append((time.perf_counter() - start) * 1000)
    return {
        "avg_ms": round(statistics.mean(times), 3),
        "p95_ms": round(statistics.quantiles(times, n=100)[94], 3),
        "max_ms": round(max(times), 3),
    }


# -----------------------
# Connections
# -----------------------
mongo_client = MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client.bench

pg_conn = psycopg.connect(host="localhost", dbname="bench", user="bench", password="bench")
pg_cur = pg_conn.cursor()

# -----------------------
# Test records
# -----------------------
mongo_user = mongo_db.users.find_one()
mongo_user_id = mongo_user["_id"]
mongo_username = mongo_user["username"]

pg_cur.execute("SELECT id, username FROM users LIMIT 1")
pg_user_id, pg_username = pg_cur.fetchone()

# -----------------------
# Run benchmarks
# -----------------------
results = {
    "Q1_primary_key_read": {
        "mongo": bench(lambda: mongo_q1_find_user(mongo_db, mongo_user_id)),
        "postgres": bench(lambda: postgres_q1_find_user(pg_cur, pg_user_id)),
    },
    "Q2_indexed_filter_username": {
        "mongo": bench(lambda: mongo_q2_user_by_username(mongo_db, mongo_username)),
        "postgres": bench(lambda: postgres_q2_user_by_username(pg_cur, pg_username)),
    },
    "Q3_join_lookup": {
        "mongo": bench(lambda: mongo_q3_user_businesses(mongo_db, mongo_user_id)),
        "postgres": bench(lambda: postgres_q3_user_businesses(pg_cur, pg_user_id)),
    },
    "Q4_aggregation": {
        "mongo": bench(lambda: mongo_q4_count_businesses(mongo_db)),
        "postgres": bench(lambda: postgres_q4_count_businesses(pg_cur)),
    },
    "Q5_range_query": {
        "mongo": bench(lambda: mongo_q5_recent_users(mongo_db)),
        "postgres": bench(lambda: postgres_q5_recent_users(pg_cur)),
    },
    "Q6_insert": {
        "mongo": bench(lambda: mongo_q6_insert_user(
            mongo_db, {"_id": ObjectId(), "username": generate(size=10)}
        )),
        "postgres": bench(lambda: postgres_q6_insert_user(
            pg_cur, pg_conn, {"id": uuid.uuid4(), "username": generate(size=10)}
        )),
    },
    "Q7_update": {
        "mongo": bench(lambda: mongo_q7_update_user(mongo_db, mongo_user_id)),
        "postgres": bench(lambda: postgres_q7_update_user(pg_cur, pg_conn, pg_user_id)),
    },
    "Q8_transaction": {
        "mongo": bench(lambda: mongo_q8_transaction(mongo_db)),
        "postgres": bench(lambda: postgres_q8_transaction(pg_cur, pg_conn)),
    },
}

print(json.dumps(results, indent=2))
# مسیر فایل خروجی در ریشه پروژه
output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results.json")

# نوشتن نتایج داخل فایل
with open(output_file, "w") as f:
    json.dump(results, f, indent=2)

pg_cur.close()
pg_conn.close()
mongo_client.close()

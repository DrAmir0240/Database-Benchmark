from pymongo import MongoClient
import psycopg
from bson import ObjectId
from nanoid import generate
import uuid

# -----------------------
# MongoDB Setup
# -----------------------
mongo_client = MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client.bench

# Drop collections if exist
mongo_db.chats.drop()
mongo_db.businesses.drop()
mongo_db.users.drop()

# Seed Users (Mongo)
users = []
for _ in range(10):
    users.append({"_id": ObjectId(), "username": generate(size=8), "createdAt": None})
mongo_db.users.insert_many(users)
mongo_db.users.create_index("username", unique=True)

# Seed Businesses (Mongo)
biz_docs = []
for i, user in enumerate(users):
    biz_docs.append({
        "_id": ObjectId(),
        "user_id": user["_id"],
        "title": f"Business_{i}",
        "createdAt": None
    })
mongo_db.businesses.insert_many(biz_docs)

# -----------------------
# PostgreSQL Setup
# -----------------------
pg_conn = psycopg.connect(host="localhost", dbname="bench", user="bench", password="bench")
pg_cur = pg_conn.cursor()

# Drop tables in dependency order using CASCADE
pg_cur.execute("DROP TABLE IF EXISTS chats CASCADE")
pg_cur.execute("DROP TABLE IF EXISTS businesses CASCADE")
pg_cur.execute("DROP TABLE IF EXISTS users CASCADE")

# Create tables
pg_cur.execute("""
CREATE TABLE users (
    id uuid PRIMARY KEY,
    username text UNIQUE,
    created_at TIMESTAMP,
    updated boolean DEFAULT FALSE
)
""")

pg_cur.execute("""
CREATE TABLE businesses (
    id uuid PRIMARY KEY,
    user_id uuid REFERENCES users(id),
    title text,
    created_at TIMESTAMP,
    updated boolean DEFAULT FALSE
)
""")

pg_cur.execute("""
CREATE TABLE chats (
    id uuid PRIMARY KEY,
    business_id uuid REFERENCES businesses(id),
    title text,
    created_at TIMESTAMP
)
""")

# Indexes
pg_cur.execute("CREATE INDEX idx_users_username ON users(username)")
pg_cur.execute("CREATE INDEX idx_business_user ON businesses(user_id)")

# -----------------------
# Seed Users (Postgres)
# -----------------------
# Mapping Mongo ObjectId -> Postgres UUID
user_map = {}

for u in users:
    pg_id = uuid.uuid4()
    user_map[str(u["_id"])] = pg_id
    pg_cur.execute(
        "INSERT INTO users (id, username, created_at) VALUES (%s, %s, NOW())",
        (pg_id, u["username"])
    )

# -----------------------
# Seed Businesses (Postgres)
# -----------------------
for i, b in enumerate(biz_docs):
    pg_id = uuid.uuid4()
    pg_cur.execute(
        "INSERT INTO businesses (id, user_id, title, created_at) VALUES (%s, %s, %s, NOW())",
        (pg_id, user_map[str(b["user_id"])], b["title"])
    )

# Commit and close connections
pg_conn.commit()
pg_cur.close()
pg_conn.close()
mongo_client.close()

print("✅ Databases fully reset and initialized.")

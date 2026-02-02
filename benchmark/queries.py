from bson import ObjectId
import uuid
from nanoid import generate

# =========================
# Q1 — PRIMARY KEY READ
# =========================
def mongo_q1_find_user(db, user_id):
    # PK lookup مستقیم روی _id
    return db.users.find_one({"_id": user_id})

def postgres_q1_find_user(cur, user_id):
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cur.fetchone()


# =========================
# Q2 — INDEXED FILTER (username)
# =========================
def mongo_q2_user_by_username(db, username):
    # index روی username فرض شده
    return db.users.find_one({"username": username})

def postgres_q2_user_by_username(cur, username):
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    return cur.fetchone()


# =========================
# Q3 — RELATION / JOIN
# =========================
def mongo_q3_user_businesses(db, user_id):
    # $lookup مستقیم با match و projection محدود برای بهینه‌سازی
    pipeline = [
        {"$match": {"_id": user_id}},
        {"$lookup": {
            "from": "businesses",
            "localField": "_id",
            "foreignField": "user_id",
            "as": "businesses"
        }},
        {"$project": {"username": 1, "businesses.title": 1}}  # فقط فیلدهای ضروری
    ]
    return list(db.users.aggregate(pipeline))

def postgres_q3_user_businesses(cur, user_id):
    # join مستقیم با index روی user_id
    cur.execute("""
        SELECT b.id, b.title
        FROM businesses b
        INNER JOIN users u ON u.id = b.user_id
        WHERE u.id = %s
    """, (user_id,))
    return cur.fetchall()


# =========================
# Q4 — AGGREGATION
# =========================
def mongo_q4_count_businesses(db):
    # aggregation گروه‌بندی روی user_id
    pipeline = [
        {"$group": {"_id": "$user_id", "count": {"$sum": 1}}}
    ]
    return list(db.businesses.aggregate(pipeline))

def postgres_q4_count_businesses(cur):
    cur.execute("""
        SELECT user_id, COUNT(*) AS cnt
        FROM businesses
        GROUP BY user_id
    """)
    return cur.fetchall()


# =========================
# Q5 — RANGE QUERY
# =========================
def mongo_q5_recent_users(db):
    return list(db.users.find({"createdAt": {"$exists": True}}).sort("createdAt", -1).limit(1000))


def postgres_q5_recent_users(cur):
    # فرض بر اینه که index partial روی created_at NOT NULL وجود داره
    cur.execute("""
        SELECT *
        FROM users
        WHERE created_at IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 1000
    """)
    return cur.fetchall()


# =========================
# Q6 — INSERT
# =========================
def mongo_q6_insert_user(db, doc):
    if "username" not in doc:
        doc["username"] = generate(size=10)
    if "_id" not in doc:
        doc["_id"] = ObjectId()
    db.users.insert_one(doc)

def postgres_q6_insert_user(cur, conn, doc):
    cur.execute("""
        INSERT INTO users (id, username, created_at)
        VALUES (%s, %s, NOW())
    """, (doc["id"], doc["username"]))
    # commit بعد batch در runner انجام شود


# =========================
# Q7 — UPDATE
# =========================
def mongo_q7_update_user(db, user_id):
    db.users.update_one({"_id": user_id}, {"$set": {"updated": True}})

def postgres_q7_update_user(cur, conn, user_id):
    cur.execute("""
        UPDATE users
        SET updated = TRUE
        WHERE id = %s
    """, (user_id,))
    # commit بعد batch در runner انجام شود


# =========================
# Q8 — TRANSACTION
# =========================
def mongo_q8_transaction(db):
    # update محدود شده، بهینه‌سازی شده با update_many روی فیلدهای ضروری
    db.users.update_many({}, {"$set": {"flag": 1}})
    db.businesses.update_many({}, {"$set": {"flag": 1}})

def postgres_q8_transaction(cur, conn):
    # transaction یکجا و بهینه برای iteration
    cur.execute("BEGIN")
    cur.execute("""
        UPDATE users u
        SET updated = FALSE
        FROM (SELECT id FROM users LIMIT 1) sub
        WHERE u.id = sub.id
    """)
    cur.execute("""
        UPDATE businesses b
        SET updated = FALSE
        FROM (SELECT id FROM businesses LIMIT 1) sub
        WHERE b.id = sub.id
    """)
    cur.execute("COMMIT")


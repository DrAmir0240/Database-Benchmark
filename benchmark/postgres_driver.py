import psycopg
from config import POSTGRES_DSN

conn = psycopg.connect(POSTGRES_DSN)

def get_user_businesses(user_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM businesses WHERE user_id = %s LIMIT 20",
            (user_id,)
        )
        return cur.fetchall()

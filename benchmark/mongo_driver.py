from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.bench

def get_user_businesses(user_id):
    return list(db.businesses.find({"user": user_id}).limit(20))

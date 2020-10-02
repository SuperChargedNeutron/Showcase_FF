import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get("MONGODB_URI")
client = pymongo.MongoClient(MONGO_URI)
db = client.DFS
player_coll = db['Player_Data']
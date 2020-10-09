import os
import pymongo

MONGO_URI = os.environ.get("MONGODB_URI")
client = pymongo.MongoClient(MONGO_URI)
db = client.DFS
player_coll = db["Player_Data"]
vegas_coll = db["Vegas_Data"]
team_coll = db["Team_Acronyms"]

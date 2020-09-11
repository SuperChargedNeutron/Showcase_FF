import os
from pymongo import MongoClient
import pymongo


MONGO_URI = os.environ.get("MONGODB_URI")
client = MongoClient(MONGO_URI)

db = client.DFS

player_coll = db["Player_Data"]
vegas_coll = db["Vegas_Data"]
TeamBuilder = db["Team_Builder"]
CalcCollection = db["CalculatorCollection"]

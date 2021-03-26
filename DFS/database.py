import os
from pymongo import MongoClient

# gets connections from environement and connects to database
MONGO_URI = os.environ.get("MONGODB_URI")

#initiliazes the db client
client = MongoClient(MONGO_URI)

# select DFS database
db = client.showcase_db

# assign collections to variables names
player_coll = db["Player_Data"]
vegas_coll = db["Vegas_Data"]
team_coll = db["Team_Acronyms"]
TeamBuilder = db["Team_Builder"]

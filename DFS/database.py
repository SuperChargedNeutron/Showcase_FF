
import os
from pymongo import MongoClient
import pymongo

client = MongoClient('localhost', 27017)

db = client.test_database
TeamBuilder = db['Team_Builder']
SS_Data = db['Saber_Sim_Data']
_4f4_Proj = db['_4for4_Projection_Data']
_4f4_Ceil = db['_4for4_Ceiling_Data']
_4f4_WR_cb = db['_4for4_WR_cb']
_4f4_RedZ = db['_4for4__RedZone_Data']
_4f4_WR_fp = db['_4for4_WR_fantasy_points']
_4f4_RB_fp = db['_4for4_RB_fantasy_points']
_4f4_RB_tar = db['_4for4_RB_target']
airy_WR = db['AirY_WR']
airy_TE = db['AirY_TE']
ETR_Ceil = db['ETR_Ceiling']

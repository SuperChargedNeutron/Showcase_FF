import pymongo
from .database import player_coll
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import numpy as np

def top_guns_query(pos, thresh, current_week, current_season):
    return list(
        player_coll.find(
            {"position": pos, 'season':current_season, "week": current_week, "C_Proj": {"$gte": int(thresh)}},
            {"_id": False, "player": True, "C_Proj": True, "C_Ceil": True, "FAV": True},
        )
    )

def pull_scaled_data(columns, meta):

    ### queries the database for the data selected and
    ### scales the columns with both scalers
    ### function returns tuple of list of lists
    ### ready to be weighted and averaged

    query_cols = {"_id": False, "player": True}
    query_params = {
        "season": int(meta["season"]),
        "week": int(meta["week"]),
        "position": meta["pos"],
    }
    for col in columns:
        query_cols.update({col: True})
        query_params.update({col: {"$exists": True}})

    query = list(player_coll.find(query_params, query_cols))
    players = [x["player"] for x in query]
    to_be_scaled = np.array([[x[key] for key in columns] for x in query])

    minmax_scaler = MinMaxScaler()
    standard_scaler = StandardScaler()

    minmax_data = dict(
        zip(players, [list(x) for x in minmax_scaler.fit_transform(to_be_scaled)])
    )
    standard_data = dict(
        zip(players, [list(x) for x in standard_scaler.fit_transform(to_be_scaled)])
    )

    return minmax_data, standard_data


def weigh_data(weights, data):

    ### this functions takes in the weights
    ### and one of the list of lists from
    ### `pull_scaled_data

    weighed_scaled_data = []
    for key in data.keys():
        player_transform = {"name": key}
        weighed_point = 0
        for i in range(len(weights)):
            num = weights[i] * data[key][i]
            weighed_point += num
        player_transform.update({"value": weighed_point})
        weighed_scaled_data.append(player_transform)
    return weighed_scaled_data


def get_raw_data(player_coll, cols):
    query_params = {col: {"$exists": True} for col in cols}
    data_return = {col: True for col in cols}
    data_return.update({"_id": False})
    data = player_coll.find(query_params, data_return)
    return data


def stack_app_query(player_coll, current_week):
    ## leave week 16 until `current_week` data is avail
    query_params = {
        "week": current_week,
        "C_Proj": {"$exists": True},
        "C_Fl": {"$exists": True},
        "C_Ceil": {"$exists": True},
        "price": {"$exists": True},
        "afpa": {"$exists": True},
    }
    data = list(
        player_coll.find(
            query_params,
            {
                "_id": False,
                "player": True,
                "position": True,
                "price": True,
                "C_Proj": True,
                "afpa": True,
                "C_Fl": True,
                "C_Ceil": True,
            },
        )
    )

    return data


def average_row(row, avgee):

    ### takes in a player/document and scans
    ### for 'proj' in columns, then avg all
    ##E the collected columns based on the averagee
    ### avgee SHOULD be 'proj' or 'ceil' or 'flr'

    acc = 0
    count = 0
    for key in row.keys():

        if (
            avgee in key.lower()
            and key.lower() != "proj_own"
            and "1k" not in key.lower()
            and "val" not in key.lower()
            and "dollar" not in key.lower()
        ):
            count += 1 if row[key] != "nan" else 0
            acc += row[key] if row[key] != "nan" else 0
    if count != 0:
        avg = acc / count
        player_coll.update_one(
            {"_id": row["_id"]}, {"$set": {f"C_{avgee.capitalize()}": round(avg, 2)}}
        )


def is_favorite(doc):
    ## this function takes in a player
    ## team, and week and determines
    ## whether that team is a favorite or
    ## not according to vegas dash
    if doc["team"] == "OAK":
        doc["team"] = "LV"
    if doc["team"] == "LA":
        doc["team"] = "LAC"
    if doc["team"] == "JAC":
        doc["team"] = "JAX"
    player_team = list(team_coll.find({"Acronym": doc["team"]}, {"_id": False}))[0]
    if len(list(vegas_coll.find({"FAV": player_team["Team"]}))) > 0:
        player_coll.update_one({"_id": doc["_id"]}, {"$set": {"FAV": True}})
    elif len(list(vegas_coll.find({"FAV": player_team["Team"]}))) == 0:
        player_coll.update_one({"_id": doc["_id"]}, {"$set": {"FAV": False}})

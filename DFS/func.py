import pymongo
from .database import _4f4_RedZ
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import numpy as np

def pull_scaled_data(columns, meta):
    query_cols = {'_id':False, 'Player':True}
    for col in columns:
        query_cols.update({col:True})
   
    query = [
        x for x in _4f4_RedZ.find(
        {'Season' : int(meta['season']), 'Week' : int(meta['week']), 'Pos':meta['pos']},
        query_cols)
        ]

    players = [x['Player'] for x in query]
    to_be_scaled = np.array([[x[key] for key in columns] for x in query])

    minmax_scaler = MinMaxScaler()
    standard_scaler = StandardScaler()

    minmax_data = dict(zip(players, 
        [list(x) for x in minmax_scaler.fit_transform(to_be_scaled)]))
    standard_data = dict(zip(players, 
        [list(x) for x in standard_scaler.fit_transform(to_be_scaled)]))

    return minmax_data, standard_data

def weigh_data(weights, data):
    weighed_scaled_data = []
    for key in data.keys():
        player_transform = {'name' : key}
        weighed_point = 0
        for i in range(len(weights)):
            num = weights[i] * data[key][i]
            weighed_point += num
        player_transform.update({'value' : weighed_point})
        weighed_scaled_data.append(player_transform)
    return weighed_scaled_data

def get_raw_data(table):
    doc_count = table.count_documents(filter={})
    data = [dict(i) for i in table.find({}, {"_id": False})[0:doc_count]]
    return data

def stack_app_query(_4f4_Ceil):
    data = []
    doc_count = _4f4_Ceil.count_documents(filter=({}))
    cursor = _4f4_Ceil.find(
        {},
        {
            "_id": False,
            "Player": True,
            "Pos": True,
            "DK_Price": True,
            "DK_Proj": True,
            "aFPA": True,
            "DK_Flr": True,
            "DK_Ceil": True,
        },
    )
    for i in range(doc_count):
        data.append(cursor[i])

    return data


def position_names(pos, db):
    data = []

    for collection in db.list_collection_names():
        col = db[collection]
        positions = ["Pos", "Position", "position"]
        for fil in positions:
            doc_count = col.count_documents(filter={fil: pos})
            if doc_count > 0:
                cursor = col.find({fil: pos}, {"_id": False})
                for i in range(doc_count):
                    data.append(cursor[i])
    names = []
    for row in data:
        if "full_name" in row:
            name = row["full_name"]
            if not any(word in name for word in names):
                names.append(name)
        elif "Name" in row:
            name = row["Name"]
            if not any(word in name for word in names):
                names.append(name)
        elif "Player" in row:
            name = row["Player"]
            if not any(word in name for word in names):
                names.append(name)
    return names


def player_query(player, db):
    player_info = {"name": player}

    for collection in db.list_collection_names():
        col = db[collection]
        name_forms = ["Name", "Player", "full_name"]
        for nm in name_forms:
            doc_count = col.count_documents(filter={nm: player})
            if doc_count > 0:
                cursor = col.find({nm: player}, {"_id": False, nm: False})
                for i in range(doc_count):
                    player_info.update(cursor[i])

    return player_info


# Python Imports
import os
from datetime import datetime
from random import randint
from time import sleep

# Third Party Imports
import pymongo
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from webdriver_manager.firefox import GeckoDriverManager

# Local Imports 
from .database import player_coll, team_coll, vegas_coll



def search_index_keys(columns):
    index_cols = []
    if "player" in columns:
        index_cols.append("player")
    if "week" in columns:
        index_cols.append("week")
    if "season" in columns:
        index_cols.append("season")
    if "position" in columns:
        index_cols.append("position")
    if "Home" in columns:
        index_cols.append("Home")
    if "Road" in columns:
        index_cols.append("Road")
    return index_cols


def conditional_insert(collection, row):
    index_cols = search_index_keys(list(row.keys()))
    query_params = {
        ic: row[ic] if not isinstance(row[ic], (np.int64, np.int32)) else int(row[ic])
        for ic in index_cols
    }
    player_row = list(collection.find(query_params, {"_id": False}))
    if len(player_row) != 0:
        for key in row:
            if key in player_row[0] and row[key] == player_row[0][key]:
                pass
            elif key not in player_row[0] and row[key] != None:
                if isinstance(row[key], (np.int32, np.int64)):
                    collection.update_one(query_params, {"$set": {key: int(row[key])}})
                else:
                    collection.update_one(query_params, {"$set": {key: row[key]}})
    elif len(player_row) == 0:
        for x in row:
            if isinstance(row[x], (np.int32, np.int64)):
                row[x] = int(row[x])
            elif isinstance(row[x], np.float64):
                row[x] = float(row[x])

        collection.insert_one(row)


def top_guns_query(pos, thresh, current_week, current_season):
    return list(
        player_coll.find(
            {
                "position": pos,
                "season": current_season,
                "week": current_week,
                "C_Proj": {"$gte": int(thresh)},
            },
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

    print(to_be_scaled)

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


def stack_app_query(player_coll, current_week, current_season):
    query_params = {
        "week": current_week,
        "season": current_season,
        "C_Proj": {"$exists": True},
        "C_Floor": {"$exists": True},
        "C_Ceil": {"$exists": True},
        "salary": {"$exists": True},
    }
    data = list(
        player_coll.find(
            query_params,
            {
                "_id": False,
                "player": True,
                "position": True,
                "salary": True,
                "C_Proj": True,
                "afpa_4f4": True,
                "C_Floor": True,
                "C_Ceil": True,
            },
        )
    )

    return data

def get_bookie_divs(dl_path):
    """ 
    Returns game divs found in mybookie.au

    Opens up a selenium browser and parses 
    the page source with beautiful soup
    """
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.download.useDownloadDir", True)
    profile.set_preference("browser.helperApps.neverAsk.openFile", True)
    profile.set_preference("browser.download.dir", dl_path)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")

    browser = webdriver.Firefox(firefox_profile=profile, executable_path=GeckoDriverManager().install())
    browser.get("https://mybookie.ag/sportsbook/nfl/")
    html = browser.page_source
    browser.close()
    soup = BeautifulSoup(html, "html.parser")
    return soup.find_all("div", {"class": "game-line py-3"})[0:16]


def scrape_bookie_divs(divs):
    game_data = []
    week_list = []

    # loop though all divs from scrape_bookie()
    for maindiv in divs:
        vegas_row = {}

        # check if div has game metadata
        if maindiv.find("meta") != None:
            try:
                teams = (
                    maindiv.find("meta", {"itemprop": "name"}).get("content").split(" v ")
                )

                date = maindiv.find("meta", {"itemprop": "startDate"}).get("content")

                py_date = datetime.strptime(date, "%Y-%m-%d %H:%M+00:%S")
                if len(maindiv.find_all("p", {"class": "game-line__banner mb-2"})) > 0:
                    banners = maindiv.find_all("p", {"class": "game-line__banner mb-2"})
                    for ban in banners:
                        
                        words = ban.text.lower().split()
        
                        if "week" in words:
                            week_ind = words.index("week")
                            week = int(words[week_ind + 1])
                            week_list.append(week)
                            break
                        else:
                            week = week_list[0] if len(week_list) > 0 else 0

                buttons = [x.text.strip() for x in maindiv.find_all("button")]

                market_ou = buttons[2].split()[1]
                market_ou = int(market_ou[0:2]) + 0.5 if market_ou[-1] == "½" else market_ou
                spread = buttons[0].split()[0]
                
                if len(spread) > 3:
                    spread = (
                        abs(int(spread[1:3]) + 0.5)
                        if spread[-1] == "½"
                        else abs(int(spread[1:3]))
                    )
                elif len(spread) == 3:
                    spread = (
                        abs(int(spread[1:2]) + 0.5)
                        if spread[-1] == "½"
                        else abs(int(spread[1:2]))
                    )
                vegas_row.update(
                    {
                        "Home": teams[0],
                        "Road": teams[1],
                        "week": int(week),
                        "season": py_date.year,
                        "Game Date": f"{py_date.month}-{py_date.day}",
                        "Market_O/U": float(market_ou),
                        "Market Spread": 0 if spread == "PK" else abs(float(spread)),
                    }
                )

                if buttons[0][0] == "-":
                    fave_team = vegas_row["Home"]
                    dog_team = vegas_row["Road"]
                elif buttons[3][0] == "-":
                    fave_team = vegas_row["Road"]
                    dog_team = vegas_row["Home"]
                vegas_row.update(
                    {
                        "FAV": fave_team,
                        "DOG": dog_team,
                        "Market_Imp_fav": (int(market_ou) / 2)
                        if spread == "PK"
                        else (int(market_ou) / 2) + (abs(int(spread)) / 2),
                        "Market_Imp_dog": (int(market_ou) / 2)
                        if spread == "PK"
                        else (int(market_ou) / 2) - (abs(int(spread)) / 2),
                    }
                )

                game_data.append(vegas_row)
            except:
                pass

    return sorted(game_data, key=lambda k: k["Market_O/U"], reverse=True)

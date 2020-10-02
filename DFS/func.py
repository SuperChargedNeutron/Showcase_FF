import pymongo
from database import player_coll, team_coll, vegas_coll
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import numpy as np
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import os
from webdriver_manager.firefox import GeckoDriverManager
from random import randint
from time import sleep

def rename_file(file, week, season):

    return f"{file}_W{week}_{season}"
    
def rename_scrape_csv(file_name, week, season, scrape, dl_path):
    recent_file = max(list(os.scandir(os.getcwd())), key=os.path.getctime).name

    if scrape == True and recent_file[-7:] != f"W{week}_{season}":
        os.rename(recent_file, os.path.join(dl_path, f"{file_name}.csv"))

def login(url, login_button, submit_login, login_user, login_pass, download_path):
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.download.useDownloadDir", True)
    profile.set_preference("browser.helperApps.neverAsk.openFile", True)
    profile.set_preference("browser.download.dir", download_path)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
    browser = webdriver.Firefox(firefox_profile=profile, executable_path=GeckoDriverManager().install())
    browser.get(url)
    sleep(3)
    browser.find_element_by_xpath(login_button).click()
    sleep(3)
    user_name = browser.find_element_by_id(login_user)
    password = browser.find_element_by_id(login_pass)
    for x in os.environ['joe_mail']:
        user_name.send_keys(x)
        sleep(np.random.rand())
    for x in os.environ['joe_pass']:
        password.send_keys(x)
        sleep(np.random.rand())
    
    browser.find_element_by_id(submit_login).click()
    sleep(3)
    return browser

def scrape_csv(browser, url, dl_button):

    browser.get(url)
    browser.implicitly_wait(5)
    browser.get(url)
    try:
        browser.find_element_by_css_selector('.close').click()
    except:
        pass

    try:
        browser.find_element_by_xpath(dl_button).click()
        scrape = True
    except:
        scrape = False

    browser.close()

    return scrape

def column_clean(column, source=""):
    if column == "name" or column == "full_name" or column == 'player':
        return "player"
    elif column == "opp" or column == 'opponent':
        return "opponent"
    elif column == "tm" or column == "teamabbrev" or column == 'team':
        return "team"
    elif column == "pos" or column == "dk position" or column == 'position':
        return "position"
    elif column == "value.1":
        return f"value1_{source}"
    elif column != "week" and column != "season":
        if source != "":
            return f"{column}_{source}"
        else:
            return column
    else:
        return column


def Filter(string):
    substr = [".", """'"""]
    return [st for st in string if not any(sub in st for sub in substr)]


def upload_file_clean(df, suffix=''):
    df.columns = [column_clean(x.lower(), source=suffix) for x in df.columns]
    name_index = list(df.columns).index("player")
    pos_index = list(df.columns).index("position") if "position" in df.columns else None
    opp_index = list(df.columns).index("opponent") if "opponent" in df.columns else None
    oak_index = df.index[df["team"] == "OAK"]
    la_index = df.index[df["team"] == "LA"]
    jax_index = df.index[df["team"] == "JAC"]

    df.loc[oak_index, "team"] = "LV"
    df.loc[la_index, "team"] = "LAC"
    df.loc[jax_index, "team"] = "JAX"

    df.iloc[:, name_index] = df.iloc[:, name_index].apply(
        lambda x: str("").join(Filter(list(x)))
    )
    df.iloc[:, name_index] = df.iloc[:, name_index].apply(
        lambda x: x.replace("III", "")
        .replace("II", "")
        .replace("IV", "")
        .replace("V", "")
        .replace("Jr", "")
        .strip()
        if x[-1] == "V"
        else x.replace("III", "")
        .replace("II", "")
        .replace("IV", "")
        .replace("Jr", "")
        .strip()
    )
    if pos_index != None:
        dst_index = df.index[df["position"] == "DST"]
        df.loc[dst_index, "position"] = "DEF"
        df.iloc[:, pos_index] = df.iloc[:, pos_index].apply(lambda x: x.split("/")[0])
        for i in df.index[df['position'] =='DEF']:
            df.iloc[i, name_index] = list(team_coll.find({'Acronym': df.iloc[i, list(df.columns).index('team')]}, {'_id':False, 'Team':True}).limit(1))[0]['Team']
    if opp_index != None:
        df.iloc[:, opp_index] = df.iloc[:, opp_index].apply(lambda x: x.replace("@", ""))

    return df


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


circleColors = [
    "#B31217",
    "#B35F12",
    "#B8A211",
    "#12B816",
    "#1450B5",
    "#1FA5B8",
    "#ADB87D",
    "#B87DB7",
    "#AABDB1",
    "#99A7BD",
]


def stack_app_query(player_coll, current_week, current_season):
    ## leave week 16 until `current_week` data is avail
    print(current_week)
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


def average_row(row, avgee):

    ### takes in a player/document and scans
    ### for 'proj' in columns, then avg all
    ##E the collected columns based on the averagee
    ### avgee SHOULD be 'proj' or 'ceil' or 'flr'

    acc = 0
    count = 0
    for key in row.keys():
        if avgee =='proj':
            if key in ['proj_4f4', 'ffpts_4f4', 'dk projection_ETR']:
                count += 1 if row[key] != 'nan' else 0
                acc += row[key] if row[key] != 'nan' else 0
        elif avgee == 'floor':
            if key in ['floor_4f4']:
                count += 1 if row[key] != 'nan' else 0
                acc += row[key] if row[key] != 'nan' else 0
        elif avgee == 'ceil':
            if key in ['ceiling_4f4']:
                count += 1 if row[key] != 'nan' else 0
                acc += row[key] if row[key] != 'nan' else 0
    if count != 0:
        avg = acc / count
        player_coll.update_one(
            {'_id':row['_id']}, 
            {'$set':{f'C_{avgee.capitalize()}': round(avg,2)}}
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


def get_bookie_divs():
    browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    browser.get("https://mybookie.ag/sportsbook/nfl/")
    html = browser.page_source
    browser.close()
    soup = BeautifulSoup(html, "html.parser")
    return soup.find_all("div", {"class": "game-line py-3"})[0:16]


def scrape_bookie_divs(divs):
    game_data = []
    week_list = []
    for maindiv in divs:
        vegas_row = {}
        if maindiv.find("meta") != None:
            teams = (
                maindiv.find("meta", {"itemprop": "name"}).get("content").split(" v ")
            )

            date = maindiv.find("meta", {"itemprop": "startDate"}).get("content")

            py_date = datetime.strptime(date, "%Y-%m-%d %H:%M+00:%S")
            if len(maindiv.find_all("p", {"class": "game-line__banner mb-2"})) > 0:
                banners = maindiv.find_all("p", {"class": "game-line__banner mb-2"})
                for ban in banners:
                    print(ban.text)
                    words = ban.text.lower().split()
                    print(words)
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
            print(buttons)
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

    return sorted(game_data, key=lambda k: k["Market_O/U"], reverse=True)

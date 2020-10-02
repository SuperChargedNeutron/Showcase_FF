import os 
import pymongo
from database import player_coll
from selenium import webdriver
from datetime import datetime
from webdriver_manager.firefox import GeckoDriverManager
from random import randint
from time import sleep
import numpy as np

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

# Python Imports
import os, glob
from datetime import datetime
from random import randint
from time import sleep

# Third Party Imports
import numpy as np
import pymongo
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager

# Local Imports
from database import player_coll, team_coll, vegas_coll


def scrape_airyards(dl_path, week, season):
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.download.useDownloadDir", True)
    profile.set_preference("browser.helperApps.neverAsk.openFile", True)
    profile.set_preference("browser.download.dir", dl_path)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")

    ## ---- HTML element XPath strings ---- ##
    year_input_xpath = '//*[@id="year-selectized"]'
    week_input_xpath = '//*[@id="weeks-selectized"]'
    dl_button_xpath = '//*[@id="download"]'
    rb_check_xpath = "/html/body/div[1]/div[2]/div[1]/div/div/div[2]/label/input"
    # wr_check_xpath = "/html/body/div[1]/div[2]/div[1]/div/div/div[3]/label/input"
    te_check_xpath = "/html/body/div[1]/div[2]/div[1]/div/div/div[4]/label/input"

    try:
        ## ---- initialize the browser and go to data URL ---- ##
        browser = webdriver.Firefox(
            firefox_profile=profile, executable_path=GeckoDriverManager().install()
        )
        browser.get("https://apps.airyards.com/airyards-2020")
        sleep(10)

        year_input = browser.find_element_by_xpath(year_input_xpath)
        year_input.send_keys(Keys.BACKSPACE)
        year_input.send_keys(season)
        year_input.send_keys(Keys.ENTER)
        sleep(3)

        week_input = browser.find_element_by_xpath(week_input_xpath)
        dl_button = browser.find_element_by_xpath(dl_button_xpath)
        rb_check = browser.find_element_by_xpath(rb_check_xpath)
        # wr_check = browser.find_element_by_xpath(wr_check_xpath)
        te_check = browser.find_element_by_xpath(te_check_xpath)

        ## ---- Navigate the Webpage ---- ##

        ## ---- clear current weeks and set correct weeks ---- ##
        week_input.click()
        for i in range(18):
            week_input.send_keys(Keys.BACKSPACE)
        weeks = list(range(week - 3, week + 1))
        for x in weeks:
            week_input.send_keys(x, Keys.ENTER)

        ## ---- set the position metric --- ##
        rb_check.click()
        te_check.click()

        ## ---- download the file --- ###
        dl_button.click()

        browser.close()

        scrape = True
    except:
        scrape = False

    return scrape


def login(url, login_button, submit_login, login_user, login_pass, download_path):
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.download.useDownloadDir", True)
    profile.set_preference("browser.helperApps.neverAsk.openFile", True)
    profile.set_preference("browser.download.dir", download_path)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
    browser = webdriver.Firefox(
        firefox_profile=profile, executable_path=GeckoDriverManager().install()
    )
    browser.get(url)
    sleep(3)
    browser.find_element_by_xpath(login_button).click()
    sleep(3)
    user_name = browser.find_element_by_id(login_user)
    password = browser.find_element_by_id(login_pass)
    for x in os.environ["joe_mail"]:
        user_name.send_keys(x)
        sleep(np.random.rand())
    for x in os.environ["joe_pass"]:
        password.send_keys(x)
        sleep(np.random.rand())

    browser.find_element_by_id(submit_login).click()
    sleep(3)
    return browser


def average_row(row, avgee):

    ### takes in a player document from mongoDB (includes _id) and scans
    ### for 'proj' in columns, then avg all
    ##E the collected columns based on the averagee
    ### avgee SHOULD be 'proj' or 'ceil' or 'floor'

    acc = 0
    count = 0
    for key in row.keys():
        if avgee == "proj":
            ## add a projection metric to be averaged in the list below
            if key in ["proj_4f4", "dk projection_ETR"]:
                count += 1 if row[key] != "nan" else 0
                acc += row[key] if row[key] != "nan" else 0
        elif avgee == "floor":
            ## add floor metric to be averaged in list below
            if key in ["floor_4f4"]:
                count += 1 if row[key] != "nan" else 0
                acc += row[key] if row[key] != "nan" else 0
        elif avgee == "ceil":
            ## add ceiling metric to be averaged to the list below
            if key in ["ceiling_4f4"]:
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


def column_clean(column, source=""):
    if column == "name" or column == "full_name" or column == "player":
        return "player"
    elif column == "opp" or column == "opponent":
        return "opponent"
    elif column == "tm" or column == "teamabbrev" or column == "team":
        return "team"
    elif column == "pos" or column == "dk position" or column == "position":
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


def scrape_def_data(dl_path):
    base_url = "https://4for4.com"
    login_button = (
        "/html/body/div[2]/div/div[1]/div/div/div[4]/div/div[1]/div/div/div/a"
    )
    login_user_id = "edit-name"
    login_pass_id = "edit-pass"
    submit_login = "edit-submit--6"

    browser = login(
        base_url, login_button, submit_login, login_user_id, login_pass_id, dl_path
    )

    browser.get("https://www.4for4.com/full-impact/cheatsheet/DEF/154605/ff_nflstats")

    soup = BeautifulSoup(browser.page_source, "html.parser")
    browser.close()

    tr_tags = soup.find_all("tr")
    cols = [
        "player",
        "opponent",
        "m/u",
        "game outcome",
        "ff ppts",
        "pts allowed",
        "yds allowed",
        "sacks",
        "forced turnovers",
    ]
    trs = []
    for tr in tr_tags[1:]:
        tds = []
        for td in tr.find_all("td")[1:]:
            tds.append(td.text)
        trs.append(tds)

    return cols, trs


def rename_file(file, week, season):

    return f"{file}_W{week}_{season}.csv"


def rename_scrape_csv(file_name, week, season, scrape, dl_path):
    recent_file = max(list(os.scandir(os.getcwd())), key=os.path.getmtime).name

    if (
        scrape == True
        and recent_file[-11:] != f"W{week}_{season}.csv"
        and os.path.isfile(f"{file_name}_W{week}_{season}.csv") == False
    ):
        os.rename(
            recent_file, os.path.join(dl_path, f"{file_name}_W{week}_{season}.csv")
        )

        renamed = True
    else:
        renamed = False

    return {"file": file_name, "scraped": scrape, "renamed": renamed}


def scrape_csv(browser, url, dl_button):

    browser.get(url)
    browser.implicitly_wait(5)
    browser.get(url)

    try:
        browser.find_element_by_xpath(dl_button).click()
        scrape = True
    except:
        scrape = False

    return scrape


def Filter(string):
    substr = [".", """'"""]
    return [st for st in string if not any(sub in st for sub in substr)]


def upload_file_clean(df, suffix=""):
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
        for i in df.index[df["position"] == "DEF"]:
            df.iloc[i, name_index] = list(
                team_coll.find(
                    {"Acronym": df.iloc[i, list(df.columns).index("team")]},
                    {"_id": False, "Team": True},
                ).limit(1)
            )[0]["Team"]
    if opp_index != None:
        df.iloc[:, opp_index] = df.iloc[:, opp_index].apply(
            lambda x: x.replace("@", "")
        )

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
    # search dict for indexer keys
    index_cols = search_index_keys(list(row.keys()))

    # set params for player search query
    query_params = {
        ic: row[ic] if not isinstance(row[ic], (np.int64, np.int32)) else int(row[ic])
        for ic in index_cols
    }
    # player search to either replace data or initialize a document
    player_row = list(collection.find(query_params, {"_id": False}))
    #replaces data
    if len(player_row) != 0:
        for key in row:
            if key in player_row[0] and row[key] == player_row[0][key]:
                pass
            elif (key not in player_row[0] or row[key] == player_row[0][key]) and row[key] != None:
                if isinstance(row[key], (np.int32, np.int64)):
                    collection.update_one(query_params, {"$set": {key: int(row[key])}})
                else:
                    collection.update_one(query_params, {"$set": {key: row[key]}})
    # starts new document
    elif len(player_row) == 0:
        for x in row:
            if isinstance(row[x], (np.int32, np.int64)):
                row[x] = int(row[x])
            elif isinstance(row[x], np.float64):
                row[x] = float(row[x])

        collection.insert_one(row)
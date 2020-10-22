## Python Packages
import os, glob, datetime
from time import sleep

## Third Party Packages
from flask import Flask, render_template, redirect, request, url_for, jsonify, session
from flask_bootstrap import Bootstrap
from flask_cors import CORS
import pandas as pd

## Local Imports
from models import FileSubmitForm, GetTimeForm
from database import db, player_coll
from scrape_func import (
    rename_scrape_csv,
    conditional_insert,
    login,
    scrape_csv,
    upload_file_clean,
    column_clean,
    average_row,
    is_favorite,
    scrape_airyards,
    scrape_def_data,
)

##  App object initialization
app = Flask(__name__, static_url_path="/static")
app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
CORS(app)
Bootstrap(app)

##  Home Route  ##
@app.route("/")
def root():
    return redirect("/get_time")

### uses forms to set week and season used by mongo queries ###
@app.route("/get_time", methods=["GET", "POST"])
def get_time():
    form = GetTimeForm(request.form)
    if form.validate():
        session["current_week"] = int(form.week.data)
        session["current_season"] = int(form.season.data)

        return redirect("/scrape_center")
    return render_template("gettime.html", form=form)

### displays all scrape buttons and uses a form for file upload
@app.route("/scrape_center", methods=["GET", "POST"])
def scrape_center():
    dl_path = os.path.join(os.environ["USERPROFILE"], "Desktop", "DFS_data")
    if not os.path.exists(dl_path):
        os.makedirs(dl_path)
    os.chdir(dl_path)
    files = [x.name for x in os.scandir(os.getcwd())]
    form = FileSubmitForm(choices=files)

    if form.validate():
        return redirect(f"/fupload/{form.file_name.data}")

    return render_template("scrape_center.html", form=form)

### sets download button and URL settings for 4f4 
### based on the button clicked
@app.route("/scrape/<file_name>")
def scrape_it(file_name):
    week = session["current_week"]
    season = session["current_season"]
    dl_path = os.path.join(
        os.path.join(os.environ["USERPROFILE"]), "Desktop", "DFS_data"
    )
    if not os.path.exists(dl_path):
        os.makedirs(dl_path)
    os.chdir(dl_path)

    # setings for 4f4 projectio
    if file_name == "4f4_projection":
        url = "https://www.4for4.com/full-impact/cheatsheet/QB/154605/ff_nflstats"
        dl_button = (
            '//*[@id="block-system-main"]/div/div/div/div/div/div/div[2]/div/div[2]/a'
        )

    # settings for floor and ceailing data
    elif file_name == "4f4_fc_data":
        url = "https://www.4for4.com/floor-ceiling-projections/draftkings"
        dl_button = '//*[@id="block-system-main"]/div/div/div/div/div/div[4]/div/div/div/div[2]/div/a'

    # settings for leverage data
    elif file_name == "4f4_leverage":
        url = "https://www.4for4.com/gpp-leverage-scores"
        dl_button = '//*[@id="field_sub_tab_body-wrapper"]/a'

    # settings for rushing redzone data
    elif file_name == "4f4_rushing_redzone":
        url = "https://www.4for4.com/red-zone-stats?tab=1&sub-tab=0"
        dl_button = '//*[@id="field_sub_tab_body-wrapper"]/a'

    # settings for passing redzone data
    elif file_name == "4f4_passing_redzone":
        url = "https://www.4for4.com/red-zone-stats?tab=2&sub-tab=0"
        dl_button = '//*[@id="field_sub_tab_body-wrapper"]/a'

    # settings for receiving redzone data
    elif file_name == "4f4_receiving_redzone":
        url = "https://www.4for4.com/red-zone-stats?tab=0&sub-tab=0"
        dl_button = '//*[@id="field_sub_tab_body-wrapper"]/a'

    elif file_name == "ETR_projection":
        url = f"https://establishtherun.com/draftkings-projections/"
        dl_button = "/html/body/div[1]/div[3]/div/div[1]/div/div/article/div[2]/div[2]/table/thead/tr[1]/th/div/button"

    elif file_name == "4f4_wr_fp_L4":
        if week >= 4:
            url = f"https://www.4for4.com/tools/stat-app/ff_points/{season}/{week - 4}/{week}/ALL/WR"
        elif week < 4 and week > 0:
            url = f"https://www.4for4.com/tools/stat-app/ff_points/{season}/1/{week}/ALL/WR"
        else:
            url = None

        dl_button = (
            "/html/body/div[4]/div/div[3]/div/div[1]/div/div/div/div[4]/div[1]/a"
        )

    elif file_name == "4f4_rb_fp_L3":
        if week >= 3:
            url = f"https://www.4for4.com/tools/stat-app/ff_points/{season}/{week - 3}/{week}/ALL/RB"
        elif week < 3 and week > 0:
            url = f"https://www.4for4.com/tools/stat-app/ff_points/{season}/1/{week}/ALL/RB"
        else:
            url = None

        dl_button = (
            "/html/body/div[4]/div/div[3]/div/div[1]/div/div/div/div[4]/div[1]/a"
        )

    elif file_name == "4f4_rb_targ_L3":
        if week >= 3:
            url = f"https://www.4for4.com/tools/stat-app/targets/{season}/{week - 3}/{week}/ALL/RB"
        elif week < 3 and week > 0:
            url = (
                f"https://www.4for4.com/tools/stat-app/targer/{season}/1/{week}/ALL/RB"
            )
        else:
            url = None

        dl_button = (
            "/html/body/div[4]/div/div[3]/div/div[1]/div/div/div/div[4]/div[1]/a"
        )

    if file_name[0:3] == "4f4" and url != None:

        base_url = "https://4for4.com"
        login_button = (
            "/html/body/div[2]/div/div[1]/div/div/div[4]/div/div[1]/div/div/div/a"
        )
        login_user_id = "edit-name"
        login_pass_id = "edit-pass"
        submit_login = "edit-submit--6"

    elif file_name[0:3] == "ETR":
        base_url = "https://establishtherun.com/"
        login_button = "/html/body/div[1]/div[1]/div/div/ul/li[2]/a"
        login_user_id = "user_login"
        login_pass_id = "user_pass"
        submit_login = "wp-submit"
    try:
        browser = login(
            base_url, login_button, submit_login, login_user_id, login_pass_id, dl_path
        )
        scrape = scrape_csv(browser, url, dl_button)

        browser.close()
    except:
        scrape = False

    if scrape == True:
        rename_scrape_csv(file_name, week, season, scrape, dl_path)

        return redirect(f"/fupload/{file_name}.csv")

    else:
        message = (
            f"{file_name} didn't scrape or most recent file was already formatted."
        )
        return render_template(
            "404.html", head="Scrape Report", code=404, message=message, boo=False
        )


@app.route("/scraper/airyards")
def airyards():
    dl_path = os.path.join(
        os.path.join(os.environ["USERPROFILE"]), "Desktop", "DFS_data"
    )
    if not os.path.exists(dl_path):
        os.makedirs(dl_path)
    os.chdir(dl_path)

    scrape = scrape_airyards(
        dl_path, session["current_week"], session["current_season"]
    )

    if scrape == True:

        return redirect(url_for(fupload, 'airyards.csv'))
    else:
        message = "something went wrong scraping airyards"
        return render_template(
            "404.html", head="Scrape Report", code=404, message=message, boo=False
        )


@app.route("/scrape_4f4")
def scrape_4f4():

    week = session["current_week"]
    season = session["current_season"]
    dl_path = os.path.join(os.environ["USERPROFILE"], "Desktop", "DFS_data")
    if not os.path.exists(dl_path):
        os.makedirs(dl_path)
    os.chdir(dl_path)

    base_url = "https://4for4.com"
    login_button = (
        "/html/body/div[2]/div/div[1]/div/div/div[4]/div/div[1]/div/div/div/a"
    )
    login_user_id = "edit-name"
    login_pass_id = "edit-pass"
    submit_login = "edit-submit--6"
    proj_scrape = [
        "https://www.4for4.com/full-impact/cheatsheet/QB/154605/ff_nflstats",
        '//*[@id="block-system-main"]/div/div/div/div/div/div/div[2]/div/div[2]/a',
    ]
    fl_ce_scrape = [
        "https://www.4for4.com/floor-ceiling-projections/draftkings",
        '//*[@id="block-system-main"]/div/div/div/div/div/div[4]/div/div/div/div[2]/div/a',
    ]
    leverage_scrape_url = "https://www.4for4.com/gpp-leverage-scores"
    rush_rz_url = "https://www.4for4.com/red-zone-stats?tab=1&sub-tab=0"
    pass_rz_url = "https://www.4for4.com/red-zone-stats?tab=2&sub-tab=0"
    rec_rz_url = "https://www.4for4.com/red-zone-stats?tab=0&sub-tab=0"
    rz_lev_dl_button = '//*[@id="field_sub_tab_body-wrapper"]/a'
    fp_targ_dl_button = (
        "/html/body/div[4]/div/div[3]/div/div[1]/div/div/div/div[4]/div[1]/a"
    )
    if week >= 4:
        wr_fp_L4_url = f"https://www.4for4.com/tools/stat-app/ff_points/{season}/{week - 3}/{week}/ALL/WR"
    elif week < 4 and week > 0:
        wr_fp_L4_url = (
            f"https://www.4for4.com/tools/stat-app/ff_points/{season}/1/{week}/ALL/WR"
        )

    if week >= 3:
        rb_fp_L3_url = f"https://www.4for4.com/tools/stat-app/ff_points/{season}/{week - 2}/{week}/ALL/RB"
        rb_tar_L3_url = f"https://www.4for4.com/tools/stat-app/targets/{season}/{week - 2}/{week}/ALL/RB"
    elif week < 3 and week > 0:
        rb_fp_L3_url = (
            f"https://www.4for4.com/tools/stat-app/ff_points/{season}/1/{week}/ALL/RB"
        )
        rb_tar_L3_url = (
            f"https://www.4for4.com/tools/stat-app/target/{season}/1/{week}/ALL/RB"
        )
    try:
        browser = login(
            base_url, login_button, submit_login, login_user_id, login_pass_id, dl_path
        )

        scrape_1 = scrape_csv(browser, proj_scrape[0], proj_scrape[1])
        nam1 = rename_scrape_csv("4f4_projection", week, season, scrape_1, dl_path)

        scrape_2 = scrape_csv(browser, fl_ce_scrape[0], fl_ce_scrape[1])
        nam2 = rename_scrape_csv("4f4_fc_data", week, season, scrape_2, dl_path)

        scrape_3 = scrape_csv(browser, leverage_scrape_url, rz_lev_dl_button)
        nam3 = rename_scrape_csv("4f4_leverage", week, season, scrape_3, dl_path)

        scrape_4 = scrape_csv(browser, rush_rz_url, rz_lev_dl_button)
        nam4 = rename_scrape_csv("4f4_rushing_redzone", week, season, scrape_4, dl_path)

        scrape_5 = scrape_csv(browser, wr_fp_L4_url, fp_targ_dl_button)
        nam5 = rename_scrape_csv("4f4_wr_fp_L4", week, season, scrape_5, dl_path)

        scrape_6 = scrape_csv(browser, pass_rz_url, rz_lev_dl_button)
        nam6 = rename_scrape_csv("4f4_passing_redzone", week, season, scrape_6, dl_path)

        scrape_7 = scrape_csv(browser, rb_fp_L3_url, fp_targ_dl_button)
        nam7 = rename_scrape_csv("4f4_rb_fp_L3", week, season, scrape_7, dl_path)

        scrape_8 = scrape_csv(browser, rec_rz_url, rz_lev_dl_button)
        nam8 = rename_scrape_csv(
            "4f4_receiving_redzone", week, season, scrape_8, dl_path
        )

        scrape_9 = scrape_csv(browser, rb_tar_L3_url, fp_targ_dl_button)
        nam9 = rename_scrape_csv("4f4_rb_targ_L3", week, season, scrape_9, dl_path)

        browser.close()

        report = [nam1, nam2, nam3, nam4, nam5, nam6, nam7, nam8, nam9]
        message = f"Here is the scraping report: \n {report}"

        return render_template(
            "404.html", head="Scrape Report", code=200, message=message, boo=True
        )

    except:
        message = "Something went wrong, please try again."
        return render_template(
            "404.html", head="Scrape Report", code=404, message=message, boo=False
        )


@app.route("/fupload/<file>")
def fupload(file):
    week = session["current_week"]
    season = session["current_season"]
    dl_path = os.path.join(
        os.path.join(os.environ["USERPROFILE"]), "Desktop", "DFS_data"
    )
    os.chdir(dl_path)

    # try:
    if "golden" in file.lower():

        df = pd.read_excel(file) if file[-4:] == "xlsx" else pd.read_csv(file)
        # data = df.iloc[7:, 14:23].reset_index(drop=True)
        # data.columns = [column_clean(x.lower()) for x in df.iloc[6, 14:23]]
        data = df.iloc[7:, 10:19].reset_index(drop=True)
        data.columns = [column_clean(x.lower()) for x in df.iloc[6, 10:19]]
        data["week"] = week
        data["season"] = season
        
        golden = data[
            [
                "position",
                "player",
                "salary",
                "team",
                "avgpointspergame",
                "season",
                "week",
            ]
        ]
        clean_df = upload_file_clean(golden)
        clean_df['salary'] = pd.to_numeric(clean_df['salary'])


    elif file == f"4f4_projection_W{week}_{season}.csv":
        df = (
            pd.read_excel(file).fillna("nan")
            if file[-4:] == "xlsx"
            else pd.read_csv(file).fillna("nan")
        )
        clean_df = upload_file_clean(df, "4f4")
        clean_df = clean_df.drop(columns=["pid_4f4"])
        clean_df = clean_df[clean_df["position"] != "K"]

    elif file == f"4f4_fc_data_W{week}_{season}.csv":
        df = pd.read_csv(file).fillna("nan")
        clean_df = upload_file_clean(df, "4f4")
        clean_df = clean_df.drop(columns=["salary_4f4"])
        clean_df["proj_4f4"] = round(clean_df["floor_4f4"] + clean_df["value1_4f4"], 2)

    elif file == f"4f4_leverage_W{week}_{season}.csv":
        df = pd.read_csv(file).fillna("nan")
        clean_df = upload_file_clean(df, "4f4")
        clean_df = clean_df.drop(columns=["dk sal $_4f4"])
        clean_df["projected own%_4f4"] = clean_df["projected own%_4f4"].apply(
            lambda x: 0 if x == " " else float(x.replace("%", ""))
        )
        clean_df["cash odds_4f4"] = clean_df["cash odds_4f4"].apply(
            lambda x: 0 if x == " " else float(x.replace("%", ""))
        )
        clean_df["gpp odds_4f4"] = clean_df["gpp odds_4f4"].apply(
            lambda x: 0 if x == " " else float(x.replace("%", ""))
        )
        clean_df["implied own%_4f4"] = clean_df["implied own%_4f4"].apply(
            lambda x: 0 if x == " " else float(x.replace("%", ""))
        )

    elif file == f"4f4_passing_redzone_W{week}_{season}.csv":
        df = pd.read_csv(file).fillna("nan")
        clean_df = upload_file_clean(df, "RZ_pass")
        clean_df = clean_df.drop(columns=["team"])
        clean_df["cmp% 10_RZ_pass"] = clean_df["cmp% 10_RZ_pass"].apply(
            lambda x: 0 if x == " " else float(x.replace("%", ""))
        )
        clean_df["cmp% 20_RZ_pass"] = clean_df["cmp% 20_RZ_pass"].apply(
            lambda x: 0 if x == " " else float(x.replace("%", ""))
        )

    elif file == f"4f4_rushing_redzone_W{week}_{season}.csv":
        df = pd.read_csv(file).fillna("nan")
        clean_df = upload_file_clean(df, "RZ_rush")
        clean_df = clean_df.drop(columns=["team"])
        clean_df["%rush 20_RZ_rush"] = clean_df["%rush 20_RZ_rush"].apply(
            lambda x: 0 if x == " " else float(x.replace("%", ""))
        )
        clean_df["%rush 10_RZ_rush"] = clean_df["%rush 10_RZ_rush"].apply(
            lambda x: 0 if x == " " else float(x.replace("%", ""))
        )
        clean_df["%rush 5_RZ_rush"] = clean_df["%rush 5_RZ_rush"].apply(
            lambda x: 0 if x == " " else float(x.replace("%", ""))
        )

    elif file == f"4f4_receiving_redzone_W{week}_{season}.csv":
        df = pd.read_csv(file).fillna("nan")
        clean_df = upload_file_clean(df, "RZ_rec")
        clean_df = clean_df.drop(columns=["team"])
        clean_df["ctch% 20_RZ_rec"] = clean_df["ctch% 20_RZ_rec"].apply(
            lambda x: 0 if x == " " else float(x.replace("%", ""))
        )
        clean_df["%tgt 20_RZ_rec"] = clean_df["%tgt 20_RZ_rec"].apply(
            lambda x: 0 if x == " " else float(x.replace("%", ""))
        )
        clean_df["ctch% 10_RZ_rec"] = clean_df["ctch% 10_RZ_rec"].apply(
            lambda x: 0 if x == " " else float(x.replace("%", ""))
        )
        clean_df["%tgt 10_RZ_rec"] = clean_df["%tgt 10_RZ_rec"].apply(
            lambda x: 0 if x == " " else float(x.replace("%", ""))
        )

    elif file == f"ETR_projection_W{week}_{season}.csv":
        df = pd.read_csv(file).fillna("nan")
        clean_df = upload_file_clean(df, "ETR")
        clean_df = clean_df.drop(columns=["dk salary_ETR", "dkslateid_ETR"])
        clean_df["dk ownership_ETR"] = clean_df["dk ownership_ETR"].apply(
            lambda x: float(x.replace("%", "")) if '%' in x else 0
        )
        clean_df["week"] = week
        clean_df["season"] = season

    elif file == f"4f4_wr_fp_L4_W{week}_{season}.csv":
        df = pd.read_csv(file).fillna("nan")
        clean_df = upload_file_clean(df, "fp")
        week_cols = [col for col in clean_df.columns if col.startswith("w")]
        clean_df[week_cols] = clean_df[week_cols].applymap(
            lambda x: float(x) if x != "-" else x
        )
        clean_df["week"] = week
        clean_df["season"] = season

    elif file == f"4f4_rb_fp_L3_W{week}_{season}.csv":
        df = pd.read_csv(file).fillna("nan")
        clean_df = upload_file_clean(df, "fp")
        week_cols = [col for col in clean_df.columns if col.startswith("w")]
        clean_df[week_cols] = clean_df[week_cols].applymap(
            lambda x: float(x) if x != "-" else x
        )
        clean_df["week"] = week
        clean_df["season"] = season

    elif file == f"4f4_rb_targ_L3_W{week}_{season}.csv":
        df = pd.read_csv(file).fillna("nan")
        clean_df = upload_file_clean(df, "targ")
        week_cols = [col for col in clean_df.columns if col.startswith("w")]
        clean_df[week_cols] = clean_df[week_cols].applymap(
            lambda x: float(x) if x != "-" else x
        )
        clean_df["array_targ"] = clean_df["array_targ"].apply(
            lambda x: 0 if x == " " else float(x.replace("%", ""))
        )
        clean_df["week"] = week
        clean_df["season"] = season

    elif file == f"airyards.csv":
        df = pd.read_csv(file).fillna("nan")
        clean_df = upload_file_clean(df, "ay")
        clean_df = clean_df.drop(columns=["unnamed: 0_ay"])
        clean_df["week"] = week
        clean_df["season"] = season

    elif file == "def_scrape":
        cols, data = scrape_def_data(dl_path)
        df = pd.DataFrame(data, columns=cols)
        clean_df = upload_file_clean(df, '4f4')
        clean_df["week"] = week
        clean_df["season"] = season
    
    for i in range(len(clean_df)):
        row = clean_df.iloc[i, :].to_dict()

        if row[list(row.keys())[0]] != "nan":
            conditional_insert(player_coll, row)

    player_coll.delete_many({ 'position': {'$ne' : 'DEF'},"avgpointspergame": {"$exists": False}})

    # except:
    #     message = f"File {file} was not able to be uploaded, double check that the name corresponds to the right colums names."
    #     return render_template("404.html", head='UPLOAD ERROR', code=404, message=message, boo=False)

    return redirect("/scrape_center")


@app.route("/fupload_4f4")
def fupload_all():

    week = session["current_week"]
    season = session["current_season"]
    dl_path = os.path.join(os.environ["USERPROFILE"], "Desktop", "DFS_data")
    os.chdir(dl_path)

    uploaded_files = {"uploaded": [], "failed": []}

    for file in glob.glob("4f4*.csv"):
        try:
            if file == f"4f4_projection_W{week}_{season}.csv":
                df = (
                    pd.read_excel(file).fillna("nan")
                    if file[-4:] == "xlsx"
                    else pd.read_csv(file).fillna("nan")
                )
                clean_df = upload_file_clean(df, "4f4")
                clean_df = clean_df.drop(columns=["pid_4f4"])
                clean_df = clean_df[clean_df["position"] != "K"]

            if file == f"4f4_fc_data_W{week}_{season}.csv":
                df = pd.read_csv(file).fillna("nan")
                clean_df = upload_file_clean(df, "4f4")
                clean_df = clean_df.drop(columns=["salary_4f4"])
                clean_df["proj_4f4"] = round(
                    clean_df["floor_4f4"] + clean_df["value1_4f4"], 2
                )

            elif file == f"4f4_leverage_W{week}_{season}.csv":
                df = pd.read_csv(file).fillna("nan")
                clean_df = upload_file_clean(df, "4f4")
                clean_df = clean_df.drop(columns=["dk sal $_4f4"])
                clean_df["projected own%_4f4"] = clean_df["projected own%_4f4"].apply(
                    lambda x: 0 if x == " " else float(x.replace("%", ""))
                )
                clean_df["cash odds_4f4"] = clean_df["cash odds_4f4"].apply(
                    lambda x: 0 if x == " " else float(x.replace("%", ""))
                )
                clean_df["gpp odds_4f4"] = clean_df["gpp odds_4f4"].apply(
                    lambda x: 0 if x == " " else float(x.replace("%", ""))
                )
                clean_df["implied own%_4f4"] = clean_df["implied own%_4f4"].apply(
                    lambda x: 0 if x == " " else float(x.replace("%", ""))
                )

            elif file == f"4f4_passing_redzone_W{week}_{season}.csv":
                df = pd.read_csv(file).fillna("nan")
                clean_df = upload_file_clean(df, "RZ_pass")
                clean_df = clean_df.drop(columns=["team"])
                clean_df["cmp% 10_RZ_pass"] = clean_df["cmp% 10_RZ_pass"].apply(
                    lambda x: 0 if x == " " else float(x.replace("%", ""))
                )
                clean_df["cmp% 20_RZ_pass"] = clean_df["cmp% 20_RZ_pass"].apply(
                    lambda x: 0 if x == " " else float(x.replace("%", ""))
                )

            elif file == f"4f4_rushing_redzone_W{week}_{season}.csv":
                df = pd.read_csv(file).fillna("nan")
                clean_df = upload_file_clean(df, "RZ_rush")
                clean_df = clean_df.drop(columns=["team"])
                clean_df["%rush 20_RZ_rush"] = clean_df["%rush 20_RZ_rush"].apply(
                    lambda x: 0 if x == " " else float(x.replace("%", ""))
                )
                clean_df["%rush 10_RZ_rush"] = clean_df["%rush 10_RZ_rush"].apply(
                    lambda x: 0 if x == " " else float(x.replace("%", ""))
                )
                clean_df["%rush 5_RZ_rush"] = clean_df["%rush 5_RZ_rush"].apply(
                    lambda x: 0 if x == " " else float(x.replace("%", ""))
                )

            elif file == f"4f4_receiving_redzone_W{week}_{season}.csv":
                df = pd.read_csv(file).fillna("nan")
                clean_df = upload_file_clean(df, "RZ_rec")
                clean_df = clean_df.drop(columns=["team"])
                clean_df["ctch% 20_RZ_rec"] = clean_df["ctch% 20_RZ_rec"].apply(
                    lambda x: 0 if x == " " else float(x.replace("%", ""))
                )
                clean_df["%tgt 20_RZ_rec"] = clean_df["%tgt 20_RZ_rec"].apply(
                    lambda x: 0 if x == " " else float(x.replace("%", ""))
                )
                clean_df["ctch% 10_RZ_rec"] = clean_df["ctch% 10_RZ_rec"].apply(
                    lambda x: 0 if x == " " else float(x.replace("%", ""))
                )
                clean_df["%tgt 10_RZ_rec"] = clean_df["%tgt 10_RZ_rec"].apply(
                    lambda x: 0 if x == " " else float(x.replace("%", ""))
                )

            elif file == f"4f4_wr_fp_L4_W{week}_{season}.csv":
                df = pd.read_csv(file).fillna("nan")
                clean_df = upload_file_clean(df, "fp")
                week_cols = [col for col in clean_df.columns if col.startswith("w")]
                clean_df[week_cols] = clean_df[week_cols].applymap(
                    lambda x: float(x) if x != "-" else x
                )

            elif file == f"4f4_rb_fp_L3_W{week}_{season}.csv":
                df = pd.read_csv(file).fillna("nan")
                clean_df = upload_file_clean(df, "fp")
                week_cols = [col for col in clean_df.columns if col.startswith("w")]
                clean_df[week_cols] = clean_df[week_cols].applymap(
                    lambda x: float(x) if x != "-" else x
                )

            elif file == f"4f4_rb_targ_L3_W{week}_{season}.csv":
                df = pd.read_csv(file).fillna("nan")
                clean_df = upload_file_clean(df, "targ")
                week_cols = [col for col in clean_df.columns if col.startswith("w")]
                clean_df[week_cols] = clean_df[week_cols].applymap(
                    lambda x: float(x) if x != "-" else x
                )
                clean_df["array_targ"] = clean_df["array_targ"].apply(
                    lambda x: 0 if x == " " else float(x.replace("%", ""))
                )

            clean_df["week"] = week
            clean_df["season"] = season

            for i in range(len(clean_df)):
                row = clean_df.iloc[i, :].to_dict()
                if row[list(row.keys())[0]] != "nan":
                    conditional_insert(player_coll, row)

            uploaded_files["uploaded"].append(file)
        except:
            uploaded_files["failed"].append(file)

    player_coll.delete_many({"avgpointspergame": {"$exists": False}})

    head = "4for4 Upload Report"
    code = 200
    message = f"Here is the report: \n {uploaded_files}"

    return render_template("404.html", head=head, code=code, message=message, boo=False)


@app.route("/concensus_data")
def c_data():
    players = list(
        player_coll.find(
            {"week": session["current_week"], "season": session["current_season"]}
        )
    )
    for x in players:
        average_row(x, "proj")
        average_row(x, "ceil")
        average_row(x, "floor")
        is_favorite(x)

    return redirect("/scrape_center")

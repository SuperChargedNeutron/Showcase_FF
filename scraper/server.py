
import os
from flask import Flask, render_template, redirect, request, url_for, jsonify, session
from scrape_func import (
    rename_file,
    rename_scrape_csv,
    conditional_insert,
    login,
    scrape_csv,
    upload_file_clean,
    column_clean
)
from database import db, player_coll
import datetime
from flask_wtf import FlaskForm
from wtforms import (
    Form,
    SelectField,
    SubmitField,
)
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from wtforms.validators import InputRequired

player_coll = db["Player_Data"]
seasons = [str(x) for x in player_coll.find({}).distinct("season")]
weeks = [str(i) for i in range(1, 17)]
class GetTimeForm(FlaskForm):
    week = SelectField("Week: ", [InputRequired()], choices=list(zip(weeks, weeks)))
    season = SelectField("Season: ", choices=list(zip(seasons, seasons)))
    submit = SubmitField()


app = Flask(__name__, static_url_path="/static")
app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

CORS(app)
Bootstrap(app)

@app.route("/")
def root():
    return redirect("/get_time")


@app.route("/get_time", methods=["GET", "POST"])
def get_time():
    form = GetTimeForm(request.form)
    if form.validate():
        session["current_week"] = int(form.week.data)
        session["current_season"] = int(form.season.data)

        return redirect("/scrape_center")
    return render_template("gettime.html", form=form)

@app.route("/scrape_center")
def scrape_center():
    dl_path = os.path.join(os.environ["USERPROFILE"], "Desktop", "DFS_data")
    if not os.path.exists(dl_path):
        os.makedirs(dl_path)
    os.chdir(dl_path)
    files = [x.name for x in os.scandir(os.getcwd())]

    return render_template("scrape_center.html", files=files)

@app.route("/scrape/<file_name>")
def scrape_it(file_name):
    week = session['current_week']
    season = session['current_season']
    dl_path = os.path.join(
        os.path.join(os.environ["USERPROFILE"]), "Desktop", "DFS_data"
    )
    if not os.path.exists(dl_path):
        os.makedirs(dl_path)
    os.chdir(dl_path)
    if file_name == "4f4_projection":
        url = "https://www.4for4.com/full-impact/cheatsheet/QB/154605/ff_nflstats"
        dl_button = (
            '//*[@id="block-system-main"]/div/div/div/div/div/div/div[2]/div/div[2]/a'
        )
        file_name = rename_file(file_name, week, season)
    elif file_name == "4f4_fc_data":
        url = "https://www.4for4.com/floor-ceiling-projections/draftkings"
        dl_button = '//*[@id="block-system-main"]/div/div/div/div/div/div[4]/div/div/div/div[2]/div/a'
        file_name = rename_file(file_name, week, season)
    elif file_name == '4f4_leverage':
        url = 'https://www.4for4.com/gpp-leverage-scores'
        dl_button = '//*[@id="field_sub_tab_body-wrapper"]/a'
        file_name = rename_file(file_name, week, season)
    elif file_name == '4f4_rushing_redzone':
        url = 'https://www.4for4.com/red-zone-stats?tab=1&sub-tab=0'
        dl_button = '//*[@id="field_sub_tab_body-wrapper"]/a'
        file_name = rename_file(file_name, week, season)
    elif file_name == '4f4_passing_redzone':
        url = 'https://www.4for4.com/red-zone-stats?tab=2&sub-tab=0'
        dl_button = '//*[@id="field_sub_tab_body-wrapper"]/a'
        file_name = rename_file(file_name, week, season)
    elif file_name == '4f4_receiving_redzone':
        url = 'https://www.4for4.com/red-zone-stats?tab=0&sub-tab=0'
        dl_button = '//*[@id="field_sub_tab_body-wrapper"]/a'
        file_name = rename_file(file_name, week, season)
    elif file_name == 'ETR_projection':
        url = f"https://establishtherun.com/draftkings-projections/"
        dl_button = '/html/body/div[1]/div[3]/div/div[1]/div/div/article/div[2]/div[2]/table/thead/tr[1]/th/div/button'
        file_name = rename_file(file_name, week, season)
    elif file_name == '4f4_wr_fp_L4':
        if week >= 4:
            url = f'https://www.4for4.com/tools/stat-app/ff_points/{season}/{week - 4}/{week}/ALL/WR'
        elif week < 4 and week > 0:
            url = f'https://www.4for4.com/tools/stat-app/ff_points/{season}/1/{week}/ALL/WR'
        else:
            url = None

        dl_button = '/html/body/div[4]/div/div[3]/div/div[1]/div/div/div/div[4]/div[1]/a'
        file_name = rename_file(file_name, week, season)
    
    elif file_name == '4f4_rb_fp_L3':
        if week >= 3:
            url = f'https://www.4for4.com/tools/stat-app/ff_points/{season}/{week - 3}/{week}/ALL/RB'
        elif week < 3 and week > 0:
            url = f'https://www.4for4.com/tools/stat-app/ff_points/{season}/1/{week}/ALL/RB'
        else:
            url = None

        dl_button = '/html/body/div[4]/div/div[3]/div/div[1]/div/div/div/div[4]/div[1]/a'
        file_name = rename_file(file_name, week, season)

    elif file_name == '4f4_rb_targ_L3':
        if week >= 3:
            url = f'https://www.4for4.com/tools/stat-app/targets/{season}/{week - 3}/{week}/ALL/RB'
        elif week < 3 and week > 0:
            url = f'https://www.4for4.com/tools/stat-app/targer/{season}/1/{week}/ALL/RB'
        else:
            url = None

        dl_button = '/html/body/div[4]/div/div[3]/div/div[1]/div/div/div/div[4]/div[1]/a'
        file_name = rename_file(file_name, week, season)
    
    if file_name[0:3] == '4f4' and url != None:
        
        base_url = 'https://4for4.com'
        login_button = "/html/body/div[2]/div/div[1]/div/div/div[4]/div/div[1]/div/div/div/a"
        login_user_id = 'edit-name'
        login_pass_id = 'edit-pass'
        submit_login = 'edit-submit--6'

    elif file_name[0:3] == 'ETR':
        base_url = 'https://establishtherun.com/'
        login_button = '/html/body/div[1]/div[1]/div/div/ul/li[2]/a'
        login_user_id = 'user_login'
        login_pass_id = 'user_pass'
        submit_login = 'wp-submit'

    browser = login(
        base_url,
        login_button,
        submit_login,
        login_user_id,
        login_pass_id,
        dl_path
        )
    scrape = scrape_csv(browser, url, dl_button)

    recent_file = max(list(os.scandir(dl_path)), key=os.path.getctime).name

    if scrape == True and recent_file[-7:] != f"W{week}_{season}":
        if os.path.isfile(os.path.join(dl_path, f"{file_name}.csv")) ==  False:
            os.rename(recent_file, os.path.join(dl_path, f"{file_name}.csv"))

        return redirect(f'/fupload/{file_name}.csv')

    else:
        return "That one didn't scrape or most recent file was already formatted."


@app.route("/fupload/<file>")
def fupload(file):
    week = session['current_week']
    season = session['current_season']
    dl_path = os.path.join(
        os.path.join(os.environ["USERPROFILE"]), "Desktop", "DFS_data"
    )
    os.chdir(dl_path)

    import pandas as pd

    try:
        if "golden" in file.lower():

            df = pd.read_excel(file) if file[-4:] == "xlsx" else pd.read_csv(file)
            data = df.iloc[7:, 10:19].reset_index(drop=True)
            data.columns = [column_clean(x.lower()) for x in df.iloc[6, 10:19]]
            data['week'] = week
            data['season'] = season
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

        elif file == f"4f4_projection_W{week}_{season}.csv":
            df = pd.read_excel(file).fillna('nan') if file[-4:] == "xlsx" else pd.read_csv(file).fillna('nan')
            clean_df = upload_file_clean(df, '4f4')
            clean_df = clean_df.drop(columns=['pid_4f4'])
            clean_df = clean_df[clean_df['position'] != 'K']

        elif file == f"4f4_fc_data_W{week}_{season}.csv":
            df = pd.read_csv(file).fillna('nan')
            clean_df = upload_file_clean(df, '4f4')
            clean_df = clean_df.drop(columns=['salary_4f4'])
            clean_df['proj_4f4'] = round(clean_df['floor_4f4'] + clean_df['value1_4f4'], 2)


        elif file == f"4f4_passing_redzone_W{week}_{season}.csv":
            df = pd.read_csv(file).fillna('nan')
            clean_df = upload_file_clean(df, 'RZ_pass')
            clean_df = clean_df.drop(columns=['team'])
            clean_df['cmp% 10_RZ_pass'] = clean_df['cmp% 10_RZ_pass'].apply(lambda x:  0 if x == " " else float(x.replace('%', ''))) 
            clean_df['cmp% 20_RZ_pass'] = clean_df['cmp% 20_RZ_pass'].apply(lambda x:  0 if x == " " else float(x.replace('%', ''))) 

        elif file == f"4f4_rushing_redzone_W{week}_{season}.csv":
            df = pd.read_csv(file).fillna('nan')
            clean_df = upload_file_clean(df, 'RZ_rush')
            clean_df = clean_df.drop(columns=['team'])
            clean_df["%rush 20_RZ_rush"] = clean_df["%rush 20_RZ_rush"].apply(lambda x:  0 if x == " " else float(x.replace('%', ''))) 
            clean_df["%rush 10_RZ_rush"] = clean_df["%rush 10_RZ_rush"].apply(lambda x:  0 if x == " " else float(x.replace('%', ''))) 
            clean_df["%rush 5_RZ_rush"] = clean_df["%rush 5_RZ_rush"].apply(lambda x: 0 if x == " " else float(x.replace('%', ''))) 

        elif file == f"4f4_receiving_redzone_W{week}_{season}.csv":
            df = pd.read_csv(file).fillna('nan')
            clean_df = upload_file_clean(df, 'RZ_rec')
            clean_df = clean_df.drop(columns=['team'])
            clean_df['ctch% 20_RZ_rec'] = clean_df['ctch% 20_RZ_rec'].apply(lambda x:  0 if x == " " else float(x.replace('%', ''))) 
            clean_df['%tgt 20_RZ_rec'] = clean_df['%tgt 20_RZ_rec'].apply(lambda x:  0 if x == " " else float(x.replace('%', ''))) 
            clean_df['ctch% 10_RZ_rec'] = clean_df['ctch% 10_RZ_rec'].apply(lambda x:  0 if x == " " else float(x.replace('%', ''))) 
            clean_df['%tgt 10_RZ_rec'] = clean_df['%tgt 10_RZ_rec'].apply(lambda x:  0 if x == " " else float(x.replace('%', ''))) 


        elif file == f"ETR_projection_W{week}_{season}.csv":
            df = pd.read_csv(file).fillna('nan')
            clean_df = upload_file_clean(df, 'ETR')
            clean_df = clean_df.drop(columns=['dk salary_ETR', 'dkslateid_ETR']) 
            clean_df['dk ownership_ETR'] = clean_df['dk ownership_ETR'].apply(lambda x:  0 if x == " " else float(x.replace('%', ''))) 

        elif file == f"4f4_wr_fp_L4_W{week}_{season}.csv":
            df = pd.read_csv(file).fillna('nan')
            clean_df = upload_file_clean(df, 'fp')
            week_cols = [col for col in clean_df.columns if col.startswith('w')]
            clean_df[week_cols] = clean_df[week_cols].applymap(lambda x: float(x) if x != '-' else x)

        elif file == f"4f4_rb_fp_L3_W{week}_{season}.csv":
            df = pd.read_csv(file).fillna('nan')
            clean_df = upload_file_clean(df, 'fp')
            week_cols = [col for col in clean_df.columns if col.startswith('w')]
            clean_df[week_cols] = clean_df[week_cols].applymap(lambda x: float(x) if x != '-' else x)

        elif file == f"4f4_rb_targ_L3_W{week}_{season}.csv":
            df = pd.read_csv(file).fillna('nan')
            clean_df = upload_file_clean(df, 'targ')
            week_cols = [col for col in clean_df.columns if col.startswith('w')]
            clean_df[week_cols] = clean_df[week_cols].applymap(lambda x: float(x) if x != '-' else x)
            clean_df['array_targ'] = clean_df['array_targ'].apply(lambda x:  0 if x == " " else float(x.replace('%', ''))) 
            

        clean_df['week'] = week
        clean_df['season'] = season

        for i in range(len(clean_df)):
            row = clean_df.iloc[i, :].to_dict()
            if row[list(row.keys())[0]] != 'nan':
                conditional_insert(player_coll, row)

        player_coll.delete_many({'avgpointspergame':{'$exists':False}})
    
    except:
        return render_template('404.html', file=file)

    return redirect("/scrape_center")

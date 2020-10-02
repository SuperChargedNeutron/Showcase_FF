from flask import render_template, redirect, request, url_for, jsonify, session
from .func import (
    get_raw_data,
    stack_app_query,
    pull_scaled_data,
    weigh_data,
    top_guns_query,
    get_current_time,
    get_bookie_divs,
    scrape_bookie_divs,
    conditional_insert,
    upload_file_clean,
    column_clean,
    rename_file, 
    scrape_csv,
    average_row,
    is_favorite,
    rename_scrape_csv,
    login
)
from .database import (
    db,
    player_coll,
    vegas_coll,
    team_coll,
    TeamBuilder,
    CalcCollection,
)
from .db_cols import (
    ss_data_cols,
    _4f4_ceil_cols,
    _4f4_proj_cols,
    _4f4_rb_fp_cols,
    _4f4_rb_tar_cols,
    _4f4_redZ_cols,
    _4f4_wr_fp_cols,
    airy_te_cols,
    airy_wr_cols,
)
from .models import CalculatorForm, GetTimeForm
import json
from urllib.parse import quote, unquote
from . import app
import os

app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")


@app.route("/")
def root():
    return redirect("/get_time")


@app.route("/get_time", methods=["GET", "POST"])
def get_time():
    form = GetTimeForm(request.form)
    if form.validate():
        session["current_week"] = int(form.week.data)
        session["current_season"] = int(form.season.data)

        return redirect("/VEGAS_Dash")
    return render_template("gettime.html", form=form)


@app.route("/VEGAS_Dash")
def vegas_dash():

    week_games = list(
        vegas_coll.find(
            {"week": session["current_week"], "season": session["current_season"]},
            {"_id": False},
        )
    )
    
    ##add counter if scrape bookie fails twice
    #  then redirect to scrape center
    ## with length of week_gmaes
    headers = week_games[0].keys()
    return render_template("vegas_dash.html", data=week_games, headers=headers)


@app.route("/scrape_bookie")
def scrape_bookie():
    divs = get_bookie_divs()
    games = scrape_bookie_divs(divs)

    for g in games:
        conditional_insert(vegas_coll, g)

    return redirect("/VEGAS_Dash")


@app.route("/<pos>_Dash")
def position_dash(pos):
    return render_template("dashboard_temp.html", position=pos)


@app.route("/<pos>_data")
def position_data(pos):
    data = list(
        player_coll.find(
            {
                "season": session["current_season"],
                "week": session["current_week"],
                "position": pos,
            },
            {"_id": False},
        )
    )
    return jsonify(data)


@app.route("/<pos>_Dash/<threshold>")
def position_dash_thresh(pos, threshold):
    return render_template("dashboard_temp.html", position=pos, thresh=threshold)


@app.route("/<pos>_data/<threshold>")
def position_data_thresh(pos, threshold):
    data = list(
        player_coll.find(
            {
                "season": session["current_season"],
                "week": session["current_week"],
                "position": pos,
                "C_Proj": {"$gte": int(threshold)},
            },
            {"_id": False},
        )
    )

    return jsonify(data)


@app.route("/TOP_GUNS/<qb_thresh>/<rb_thresh>/<wr_thresh>/<te_thresh>/<def_thresh>")
def top_guns(qb_thresh, rb_thresh, wr_thresh, te_thresh, def_thresh):

    qbs = top_guns_query(
        "QB", qb_thresh, session["current_week"], session["current_season"]
    )
    rbs = top_guns_query(
        "RB", rb_thresh, session["current_week"], session["current_season"]
    )
    wrs = top_guns_query(
        "WR", wr_thresh, session["current_week"], session["current_season"]
    )
    tes = top_guns_query(
        "TE", te_thresh, session["current_week"], session["current_season"]
    )
    defs = top_guns_query(
        "DEF", def_thresh, session["current_week"], session["current_season"]
    )

    qb_headers = list(qbs[0].keys())
    rb_headers = list(rbs[0].keys())
    wr_headers = list(wrs[0].keys())
    te_headers = list(tes[0].keys())
    def_headers = list(defs[0].keys())

    return render_template(
        "topguns.html",
        qbs=qbs,
        qb_headers=qb_headers,
        rbs=rbs,
        rb_headers=rb_headers,
        wrs=wrs,
        wr_headers=wr_headers,
        tes=tes,
        te_headers=te_headers,
        defs=defs,
        def_headers=def_headers,
    )


@app.route("/stack_app", methods=["GET", "POST"])
def stack_app():
    return render_template("stack_app.html")


@app.route("/stack_app_data", methods=["GET", "POST"])
def stack_app_data():
    names = stack_app_query(
        player_coll, session["current_week"], session["current_season"]
    )
    teams = [x for x in TeamBuilder.find({}, {"_id": False})]
    data = {"names": names, "teams": teams}
    return jsonify(data)


@app.route("/<team_name>/<qb>/<rb1>/<rb2>/<wr1>/<wr2>/<wr3>/<te>/<dst>/<flex>")
def save_new_team(team_name, qb, rb1, rb2, wr1, wr2, wr3, te, dst, flex):
    team = {
        "name": " ".join(team_name.split("-")),
        "QB": " ".join(qb.split("-")),
        "RBs": [" ".join(x.split("-")) for x in [rb1, rb2]],
        "WRs": [" ".join(x.split("-")) for x in [wr1, wr2, wr3]],
        "TE": " ".join(te.split("-")),
        "DST": " ".join(dst.split("-")),
        "flex": " ".join(flex.split("-")),
    }

    TeamBuilder.insert_one(team)

    return redirect("/stack_app")


@app.route("/football_calculator_settings", methods=["GET", "POST"])
def calculator_settings():
    form = CalculatorForm(request.form)
    if form.validate():
        return redirect(
            quote(
                f"/calculator/{form.point_label.data}/{form.amnt_pts.data}/{form.position.data}/{form.season.data}/{form.week.data}"
            )
        )

    return render_template("calc_settings_jinja.html", form=form)


@app.route("/calculator/<string:label>/<int:amnt>/<position>/<season>/<week>")
def football_calculator(label, amnt, position, season, week):
    return render_template(
        "football_calc.html",
        label=label,
        amnt=amnt,
        position=position,
        season=season,
        week=week,
    )


@app.route("/<string:label>/<meta>/<weights>/<columns>")
def calculator_submit(label, meta, weights, columns):
    point_label = unquote(label)
    point_meta = json.loads(unquote(meta))
    point_weights = json.loads(unquote(weights))
    point_columns = json.loads(unquote(columns))
    point_data = {"label": point_label}
    columns = []
    weights = []
    if len(point_weights) == len(point_columns):
        for i in range(len(point_weights)):
            point_dict = {
                "weight": point_weights[i][f"weight{i+1}"],
                "col": point_columns[i][f"column{i+1}"],
            }
            columns.append(point_columns[i][f"column{i+1}"])
            weights.append(float(point_weights[i][f"weight{i+1}"]))
            point_data[f"point{i+1}"] = point_dict

    CalcCollection.insert_one(point_data)

    minmax_data, standard_data = pull_scaled_data(columns, point_meta)

    minmax_point = weigh_data(weights, minmax_data)
    standard_point = weigh_data(weights, standard_data)

    for p_minmax, p_standard in zip(minmax_point, standard_point):
        player_coll.update_many(
            {
                "player": p_minmax["name"],
                "season": int(point_meta["season"]),
                "week": int(point_meta["week"]),
                "position": point_meta["pos"],
            },
            {
                "$set": {
                    f"{label}_minmax": p_minmax["value"],
                    f"{label}_standard": p_standard["value"],
                }
            },
        )

    return redirect(f"/{point_meta['pos']}_Dash")


# @app.route('/scrape_4f4')
# def scrape_4f4():

#     week = session['current_week']
#     season = session['current_season']
#     dl_path = os.path.join(
#         os.path.join(os.environ["USERPROFILE"]), "Desktop", "DFS_data"
#     )
#     if not os.path.exists(dl_path):
#         os.makedirs(dl_path)
#     os.chdir(dl_path)
#     base_url = 'https://4for4.com'
#     login_button = "/html/body/div[2]/div/div[1]/div/div/div[4]/div/div[1]/div/div/div/a"
#     login_user_id = 'edit-name'
#     login_pass_id = 'edit-pass'
#     submit_login = 'edit-submit--6'
#     proj_scrape = [ 
#         "https://www.4for4.com/full-impact/cheatsheet/QB/154605/ff_nflstats",
#         '//*[@id="block-system-main"]/div/div/div/div/div/div/div[2]/div/div[2]/a'
#     ]
#     fl_ce_scrape = [
#         "https://www.4for4.com/floor-ceiling-projections/draftkings",
#         '//*[@id="block-system-main"]/div/div/div/div/div/div[4]/div/div/div/div[2]/div/a'
#     ]
#     leverage_scrape_url = 'https://www.4for4.com/gpp-leverage-scores',
#     rush_rz_url = 'https://www.4for4.com/red-zone-stats?tab=1&sub-tab=0',
#     pass_rz_url = 'https://www.4for4.com/red-zone-stats?tab=2&sub-tab=0'
#     rec_rz_url ='https://www.4for4.com/red-zone-stats?tab=0&sub-tab=0'
#     rz_lev_dl_button = '//*[@id="field_sub_tab_body-wrapper"]/a'
#     fp_targ_dl_button = '/html/body/div[4]/div/div[3]/div/div[1]/div/div/div/div[4]/div[1]/a'
#     if week >= 4:
#         wr_fp_L4_url = f'https://www.4for4.com/tools/stat-app/ff_points/{season}/{week - 4}/{week}/ALL/WR'
#     elif week < 4 and week > 0:
#         wr_fp_L4_url = f'https://www.4for4.com/tools/stat-app/ff_points/{season}/1/{week}/ALL/WR'

#     if week >= 3:
#         rb_fp_L3_url = f'https://www.4for4.com/tools/stat-app/ff_points/{season}/{week - 3}/{week}/ALL/RB'
#         rb_tar_L3_url = f'https://www.4for4.com/tools/stat-app/targets/{season}/{week - 3}/{week}/ALL/RB'
#     elif week < 3 and week > 0:
#         rb_fp_L3_url = f'https://www.4for4.com/tools/stat-app/ff_points/{season}/1/{week}/ALL/RB'
#         tb_tar_L3_url = f'https://www.4for4.com/tools/stat-app/targer/{season}/1/{week}/ALL/RB'

#     browser = login(
#         base_url,
#         login_button,
#         submit_login,
#         login_user_id,
#         login_pass_id,
#         dl_path
#         )
#     scrape_1 = scrape_csv(browser, proj_scrape[0], proj_scrape[1])
#     rename_scracpe_csv(f"4f4_projection_W{week}_{season}.csv", week, season)
#     scrape_2 = scrape_csv(browser, fl_ce_scrape[0], fl_ce_scrape[1])
#     rename_scracpe_csv(f"4f4_fc_data_W{week}_{season}.csv", week, season)
#     scrape_3 = scrape_csv(browser, leverage_scrape_url, rz_lev_dl_button)
#     rename_scracpe_csv(f"4f4_passing_redzone_W{week}_{season}.csv", week, season)
#     scrape_4 = scrape_csv(browser, rush_rz_url, rz_lev_dl_button)
#     rename_scracpe_csv(f"4f4_projection_W{week}_{season}.csv", week, season)
#     scrape_5 = scrape_csv(browser, pass_rz_url, rz_lev_dl_button)
#     rename_scracpe_csv(f"4f4_projection_W{week}_{season}.csv", week, season)
#     scrape_6 = scrape_csv(browser, rec_rz_url, rz_lev_dl_button)
#     rename_scracpe_csv(f"4f4_projection_W{week}_{season}.csv", week, season)
#     scrape_7 = scrape_csv(browser, wr_fp_L4_url, fp_targ_dl_button)
#     rename_scracpe_csv(f"4f4_projection_W{week}_{season}.csv", week, season)
#     scrape_8 = scrape_csv(browser, rb_fp_L3_url, fp_targ_dl_button)
#     rename_scracpe_csv(f"4f4_projection_W{week}_{season}.csv", week, season)
#     scrape_8 = scrape_csv(browser, rb_tar_L3_url, fp_targ_dl_button)
#     rename_scracpe_csv(f"4f4_projection_W{week}_{season}.csv", week, season)


@app.route('/concensus_data')
def c_data():
    players = list(player_coll.find({'week':session['current_week'], 'season':session['current_season']}))
    for x in players:
        average_row(x, 'proj')
        average_row(x, 'ceil')
        average_row(x, 'floor')
        is_favorite(x)

    return redirect('/scrape_center')

@app.route("/delete/<collection>/<name>")
def delete_team_points(collection, name):
    if collection == "teams":
        query = {"name": name}
        TeamBuilder.delete_one(query)
    elif collection == "points":
        query = {"label": name}
        CalcCollection.delete_one(query)
    return redirect("/stack_app")


@app.route("/raw_data/<source>")
def raw_data(source):
    if source == "SS_Data":
        name = "Saber Sim Raw"
        cols = ss_data_cols
    elif source == "4f4proj":
        name = "4for4 Projection Data"
        cols = _4f4_proj_cols
    elif source == "4f4ceil":
        name = "4for4 Ceiling Data"
        cols = _4f4_ceil_cols
    # elif source == '4f4_WR_cb':
    #     name = "4for4 WR cb?"
    #     cols = _4f4_wrcb_co
    elif source == "4f4_redzone":
        name = "4for4 Redzone Data"
        cols = _4f4_redZ_cols
    elif source == "4f4_WR_fp":
        name = "4for4 WR Fantasy Points"
        cols = _4f4_wr_fp_cols
    elif source == "4f4_RB_fp":
        name = "4for4 RB Fantasy Points"
        cols = _4f4_rb_fp_cols
    elif source == "4f4_RB_tar":
        name = "4for4 RB Target Data"
        cols = _4f4_rb_tar_cols
    elif source == "airy_wr":
        name = "AirY WR Data"
        cols = airy_wr_cols
    elif source == "airy_te":
        name = "AirY TE Data"
        cols = airy_te_cols

    data = get_raw_data(player_coll, cols)
    headers = data[0].keys()

    return render_template("raw_data_temp.html", name=name, data=data, headers=headers)

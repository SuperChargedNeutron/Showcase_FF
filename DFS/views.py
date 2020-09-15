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
    conditional_insert
)
from .database import (
    db,
    player_coll,
    vegas_coll,
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

@app.route("/get_time", methods=['GET', 'POST'])
def get_time():
    form = GetTimeForm(request.form)
    if form.validate():
        session['current_week'] = int(form.week.data)
        session['current_season'] = int(form.season.data)

        return redirect('/VEGAS_Dash')
    return render_template('gettime.html', form=form)

@app.route("/VEGAS_Dash")
def vegas_dash():

    week_games = list(
        vegas_coll.find(
            {"week": session["current_week"], "season": session["current_season"]},
            {"_id": False}
        )
    )
    headers = week_games[0].keys()

    return render_template("vegas_dash.html", data=week_games, headers=headers)

@app.route("/scrape_bookie")
def scrape_bookie():
    divs = get_bookie_divs()
    games = scrape_bookie_divs(divs)
    
    for g in games:
        conditional_insert(vegas_coll, g)

    return redirect('/VEGAS_Dash')

@app.route("/<pos>_Dash")
def position_dash(pos):
    return render_template("dashboard_temp.html", position=pos)


@app.route("/<pos>_data")
def position_data(pos):
    data = list(
        player_coll.find(
            {"season": session["current_season"], "week": session["current_week"], "position": pos},
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

    qbs = top_guns_query("QB", qb_thresh, session["current_week"], session["current_season"])
    rbs = top_guns_query("RB", rb_thresh, session["current_week"], session["current_season"])
    wrs = top_guns_query("WR", wr_thresh, session["current_week"], session["current_season"])
    tes = top_guns_query("TE", te_thresh, session["current_week"], session["current_season"])
    defs = top_guns_query("DEF", def_thresh, session["current_week"], session["current_season"])

    qb_headers = list(qbs[0].keys())
    rb_headers = list(rbs[0].keys())
    wr_headers = list(wrs[0].keys())
    te_headers = list(tes[0].keys())
    def_headers = list(defs[0].keys())

    # return jsonify(qbs)
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


@app.route("/stack_app")
def stack_app():
    return render_template("stack_app.html")


@app.route("/stack_app_data")
def stack_app_data():
    names = stack_app_query(player_coll, session["current_week"])
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

from flask import render_template, redirect, request, url_for, jsonify, session
from .func import (
    get_raw_data,
    position_names,
    player_query,
    stack_app_query,
    pull_scaled_data,
    weigh_data,
)
from .database import (
    db,
    player_coll,
    vegas_coll,
    TeamBuilder,
    SS_Data,
    _4f4_Proj,
    _4f4_Ceil,
    _4f4_WR_cb,
    _4f4_RedZ,
    _4f4_WR_fp,
    _4f4_RB_fp,
    _4f4_RB_tar,
    airy_WR,
    airy_TE,
    CalcCollection,
)
from .models import CalculatorForm
import json
from urllib.parse import quote, unquote
from . import app

app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = "you-will-never-guess"


@app.route("/")
def root():
    return redirect("/VEGAS_Dash")


@app.route("/VEGAS_Dash")
def vegas_dash():
    current_week = list(
        vegas_coll.find({}, {"_id": False, "Week": True}).sort("Week", -1).limit(1)
    )[0]["Week"]

    week_games = list(vegas_coll.find({"Week": current_week}, {"_id": False}))
    headers = week_games[0].keys()

    return render_template("vegas_dash.html", data=week_games, headers=headers)


@app.route("/<pos>_Dash")
def position_dash(pos):
    return render_template("dashboard_temp.html", position=pos)


@app.route("/<pos>_data")
def position_data(pos):

    players = position_names(pos, db)
    data = [player_query(player, db) for player in players]

    return jsonify(data)


@app.route("/TOP_GUNS/<qb_thresh>/<rb_thresh>/<wr_thresh>/<te_thresh>/<def_thresh>")
def top_guns(qb_thresh, rb_thresh, wr_thresh, te_thresh, def_thresh):
    current_week = list(
        vegas_coll.find({}, {"_id": False, "Week": True}).sort("Week", -1).limit(1)
    )[0]["Week"] 

    ## leave week as 16 for now
    qbs = list(player_coll.find(
        {'position':'QB', "week": 16, 'C_Proj':{'$gte':int(qb_thresh)}}, 
        {'_id':False, 'player':True, 'C_Proj':True,'C_Ceil':True, 'FAV':True}
        ))
    rbs = list(player_coll.find(
        {'position':'RB', "week": 16, 'C_Proj':{'$gte':int(rb_thresh)}}, 
        {'_id':False, 'player':True, 'C_Proj':True,'C_Ceil':True, 'FAV':True}
        ))
    wrs = list(player_coll.find(
        {'position':'WR', "week": 16, 'C_Proj':{'$gte':int(wr_thresh)}}, 
        {'_id':False, 'player':True, 'C_Proj':True,'C_Ceil':True, 'FAV':True}
        ))
    tes = list(player_coll.find(
        {'position':'TE', "week": 16, 'C_Proj':{'$gte':int(te_thresh)}}, 
        {'_id':False, 'player':True, 'C_Proj':True,'C_Ceil':True, 'FAV':True}
        ))
    defs = list(player_coll.find(
        {'position':'DEF', "week": 16, 'C_Proj':{'$gte':int(def_thresh)}}, 
        {'_id':False, 'player':True, 'C_Proj':True,'C_Ceil':True, 'FAV':True}
        ))


    qb_headers = list(qbs[0].keys())
    rb_headers = list(rbs[0].keys())
    wr_headers = list(wrs[0].keys())
    te_headers = list(tes[0].keys())
    def_headers = list(defs[0].keys())

    # return jsonify(qbs)
    return render_template('topguns.html', 
        qbs=qbs, 
        qb_headers=qb_headers,
        rbs=rbs,
        rb_headers=rb_headers,
        wrs=wrs,
        wr_headers=wr_headers,
        tes=tes,
        te_headers=te_headers,
        defs=defs,
        def_headers=def_headers
        )


@app.route("/stack_app")
def stack_app():
    return render_template("stack_app.html")


@app.route("/stack_app_data")
def stack_app_data():
    names = stack_app_query(player_coll)
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
        _4f4_Proj.update(
            {
                "Player": p_minmax["name"],
                "Season": int(point_meta["season"]),
                "Week": int(point_meta["week"]),
                "Pos": point_meta["pos"],
            },
            {
                "$set": {
                    f"{label}_minmax": p_minmax["value"],
                    f"{label}_standard": p_standard["value"],
                }
            },
        )

    return redirect(f"/{point_meta['pos']}_Dash")


@app.route("/team&points_manager")
def teampointmanager():

    team_query = TeamBuilder.find({}, {"_id": False, "name": True})
    calc_query = CalcCollection.find({}, {"_id": False, "label": True})
    team_names = [doc for doc in team_query]
    calc_labels = [doc for doc in calc_query]
    # return jsonify({ '1':team_names, '2':calc_labels})
    return render_template("data_manager.html", teams=team_names, labels=calc_labels)


@app.route("/delete/<collection>/<name>")
def delete_team_points(collection, name):
    if collection == "teams":
        query = {"name": name}
        TeamBuilder.delete_one(query)
    elif collection == "points":
        query = {"label": name}
        CalcCollection.delete_one(query)
    return redirect("/team&points_manager")


@app.route("/saber_sim_raw")
def saber_sim_raw():

    name = "Saber Sim Data"
    ss_data = get_raw_data(SS_Data)
    headers = list(ss_data[0].keys())

    return render_template(
        "raw_data_temp.html", name=name, data=ss_data, headers=headers
    )


@app.route("/4f4proj")
def _4f4proj():
    name = "4for4 Projection Data"
    _4f4_proj_data = get_raw_data(_4f4_Proj)
    headers = list(_4f4_proj_data[0].keys())

    return render_template(
        "raw_data_temp.html", name=name, data=_4f4_proj_data, headers=headers
    )


@app.route("/4f4ceil")
def _4f4ceil():
    name = "4for4 Ceiling Data"
    _4f4_ceil_data = get_raw_data(_4f4_Ceil)
    headers = list(_4f4_ceil_data[0].keys())

    return render_template(
        "raw_data_temp.html", name=name, data=_4f4_ceil_data, headers=headers
    )


@app.route("/4f4_WR_cb")
def _4f4wrcb():
    name = "4for4 WR cb?"
    _4f4_wrcb_data = get_raw_data(_4f4_WR_cb)
    headers = list(_4f4_wrcb_data[0].keys())

    return render_template(
        "raw_data_temp.html", name=name, data=_4f4_wrcb_data, headers=headers
    )


@app.route("/4f4_redzone")
def _4f4RedZ():
    name = "4for4 Redzone Data"
    _4f4_redz_data = get_raw_data(_4f4_RedZ)
    headers = list(_4f4_redz_data[0].keys())

    return render_template(
        "raw_data_temp.html", name=name, data=_4f4_redz_data, headers=headers
    )


@app.route("/4f4_WRfp")
def _4f4wrfp():
    name = "4for4 WR Fantasy Points"
    _4f4_WRfp_data = get_raw_data(_4f4_WR_fp)
    headers = list(_4f4_WRfp_data[0].keys())

    return render_template(
        "raw_data_temp.html", name=name, data=_4f4_WRfp_data, headers=headers
    )


@app.route("/4f4_RBfp")
def _4f4rbfp():
    name = "4for4 RB Fantasy Points"
    _4f4_rbfp_data = get_raw_data(_4f4_RB_fp)
    headers = list(_4f4_rbfp_data[0].keys())

    return render_template(
        "raw_data_temp.html", name=name, data=_4f4_rbfp_data, headers=headers
    )


@app.route("/4f4_rbtar")
def _4f4rbtar():
    name = "4for4 RB Target Data"
    _4f4_rbtar_data = get_raw_data(_4f4_RB_tar)
    headers = list(_4f4_rbtar_data[0].keys())

    return render_template(
        "raw_data_temp.html", name=name, data=_4f4_rbtar_data, headers=headers
    )


@app.route("/airy_wr")
def airywr():
    name = "AirY WR Data"
    airywr_data = get_raw_data(airy_WR)
    headers = list(airywr_data[0].keys())

    return render_template(
        "raw_data_temp.html", name=name, data=airywr_data, headers=headers
    )


@app.route("/airy_te")
def airyte():
    name = "AirY TE Data"
    airyte_data = get_raw_data(airy_TE)
    headers = list(airyte_data[0].keys())

    return render_template(
        "raw_data_temp.html", name=name, data=airyte_data, headers=headers
    )


@app.route("/etr_ceil")
def etrceil():
    name = "ETR Ceiling Data"
    etrceil_data = get_raw_data(ETR_Ceil)
    headers = list(etrceil_data[0].keys())

    return render_template(
        "raw_data_temp.html", name=name, data=etrceil_data, headers=headers
    )
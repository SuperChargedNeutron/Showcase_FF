# Python Imports
import os, json
from urllib.parse import quote, unquote

# Third Party Imports
from flask import render_template, redirect, request, url_for, jsonify, session

# Local Imports
from . import app
from .database import player_coll, vegas_coll, TeamBuilder
from .models import CalculatorForm, GetTimeForm
from .func import (
    stack_app_query,
    pull_scaled_data,
    weigh_data,
    top_guns_query,
    get_bookie_divs,
    scrape_bookie_divs,
    conditional_insert
)


# app configuration
app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY"
)  # necessary for get_time and calcutor forms

# Root route
@app.route("/")
def root():
    return redirect("/get_time")


# Get Time route, validates form when Submit is clicked
# then redirects with appropiate season and year variables to query ny
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

    ## this conditoinal check if there was any games returned for the current time
    if len(week_games) > 0:
        # this extracts colmns names for HTML
        headers = week_games[0].keys()

        return render_template("vegas_dash.html", data=week_games, headers=headers)

    else:
        return redirect("/scrape_bookie")


# This route scrapes mybookie.au
@app.route("/scrape_bookie")
def scrape_bookie():
    # gets game divs from HTML
    divs = get_bookie_divs()

    # extracts data from HTML divs
    games = scrape_bookie_divs(divs, session['current_week'])

    # insert into database based on values
    for g in games:
        conditional_insert(vegas_coll, g)

    return redirect("/VEGAS_Dash")


# this route handles all positional dashboards
# with ONE HTML template. Javascript gets data
# #from route right below def postion data
@app.route("/<pos>_Dash")
def position_dash(pos):
    return render_template("dashboard_temp.html", position=pos)


# queries the database based on position and current time
# then send data out in a json file to be parsed in the
# dashboard_table.js file
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


# Same idea as above this time we add a threshold to the query
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
                "C_Proj": {
                    "$gte": int(threshold)
                },  ## this is where the threshhold is added to query
            },
            {"_id": False},
        )
    )

    return jsonify(data)


## return only C_proj for players who meet the threshold.
# high default threshold is hardcoded in the HTML href (link)
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

    # this extracts colmns names for HTML
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


# This route queries both players with only
# C_proj, C_floor, and C_ceil data
# and the stacked teams created in the app
@app.route("/stack_app_data", methods=["GET", "POST"])
def stack_app_data():
    player_data = stack_app_query(
        player_coll, session["current_week"], session["current_season"]
    )
    team_data = [x for x in TeamBuilder.find({}, {"_id": False})]
    data = {"names": player_data, "teams": team_data}

    return jsonify(data)


@app.route("/stack_app", methods=["GET", "POST"])
def stack_app():
    return render_template("stack_app.html")


# This route receives team names from the
# teams created in the stack app
# and inputs the names to the team_coll collection
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


# This route renders the form that collects
# the metadata on custom points
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


# This route receives the point metadata from the calculator from
# and renders the frontend to input point weightings and columns
# necessary
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


# this route the take in metadata, weights and columns,
# each in JSON format and parses then
@app.route("/<string:label>/<meta>/<weights>/<columns>")
def calculator_submit(label, meta, weights, columns):
    # parsess data from URL
    point_meta = json.loads(unquote(meta))
    point_weights = json.loads(unquote(weights))
    point_columns = json.loads(unquote(columns))

    # extracts necessary data and reformat to list of dictionaries
    columns = []
    weights = []
    if len(point_weights) == len(point_columns):
        for i in range(len(point_weights)):
            ###### I think the commented out code is useless #######
            # point_dict = {
            #     "weight": point_weights[i][f"weight{i+1}"],
            #     "col": point_columns[i][f"column{i+1}"],
            # }
            columns.append(point_columns[i][f"column{i+1}"])
            weights.append(float(point_weights[i][f"weight{i+1}"]))

    # pulls data from database and applies normalization to the data
    # first variable returned is data scaled by maxmin and
    # second is scaled by a sttandard scaler
    minmax_data, standard_data = pull_scaled_data(columns, point_meta)

    # weigh and combine the data according the weights
    minmax_point = weigh_data(weights, minmax_data)
    standard_point = weigh_data(weights, standard_data)

    # update the database document with two new points
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


# deletes teams off the teambuilder collection
@app.route("/delete/<collection>/<name>")
def delete_team_points(collection, name):
    if collection == "teams":
        query = {"name": name}
        TeamBuilder.delete_one(query)
    return redirect("/stack_app")

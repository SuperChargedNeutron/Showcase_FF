import os
import datetime
from flask_wtf import FlaskForm
from wtforms import (
    Form,
    SelectField,
    SubmitField,
)
from wtforms.validators import InputRequired
from database import player_coll

seasons = [str(x) for x in player_coll.find({}).distinct("season")]

if None in seasons:
    seasons.pop(seasons.index(None))
positions = ["QB", "RB", "WR", "TE", "DEF"]

weeks = [str(i) for i in range(1, 17)]

dl_path = os.path.join(os.environ["USERPROFILE"], "Desktop", "DFS_data")
if not os.path.exists(dl_path):
    os.makedirs(dl_path)
os.chdir(dl_path)
files = [x.name for x in os.scandir(os.getcwd())]


class GetTimeForm(FlaskForm):
    week = SelectField("Week: ", [InputRequired()], choices=list(zip(weeks, weeks)))
    season = SelectField("Season: ", choices=list(zip(seasons, seasons)))
    submit = SubmitField()


class FileSubmitForm(FlaskForm):
    file_name = SelectField(
        "File Name : ", [InputRequired()], choices=list(zip(files, files))
    )
    submit = SubmitField()

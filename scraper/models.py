# Pthon Imports
import os, datetime

# Third Party Imports
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, DataRequired
from wtforms import (
    Form,
    StringField,
    IntegerField,
    SelectField,
    SubmitField,
)

# Local Imports
from database import player_coll

# find seasons available from player data
seasons = [str(x) for x in player_coll.find({}).distinct("season")]
if None in seasons:
    seasons.pop(seasons.index(None))

# hard code positions and week for certain options in the forms
positions = ["QB", "RB", "WR", "TE", "DEF"]
weeks = [str(i) for i in range(1, 17)]

# Sets the options for the file uploads based on current files
dl_path = os.path.join(os.environ["USERPROFILE"], "Desktop", "DFS_data")
if not os.path.exists(dl_path):
    os.makedirs(dl_path)
os.chdir(dl_path)
files = [x.name for x in os.scandir(os.getcwd())]

# Forms are used in this app for user input in certain places
# easy to tell when the form 
# is being initialized in the views.py file
class GetTimeForm(FlaskForm):
    week = SelectField("Week: ", [InputRequired()], choices=list(zip(weeks, weeks)))
    season = SelectField("Season: ", choices=list(zip(seasons, seasons)))
    submit = SubmitField()

class FileSubmitForm(FlaskForm):
    file_name = SelectField(
        "File Name : ", [InputRequired()], choices=list(zip(files, files))
    )
    submit = SubmitField()

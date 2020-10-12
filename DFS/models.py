# Pthon Imports
import datetime

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
from .database import player_coll

# find seasons available from player data
seasons = [str(x) for x in player_coll.find({}).distinct("season")]
if None in seasons:
    seasons.pop(seasons.index(None))

# hard code positions and week for certain options in the forms
positions = ["QB", "RB", "WR", "TE", "DEF"]
weeks = [str(i) for i in range(1, 17)]

# Forms are used in this app for user input in certain places
# easy to tell when the form 
# is being initialized in the views.py file
class GetTimeForm(FlaskForm):
    week = SelectField("Week: ", [InputRequired()], choices=list(zip(weeks, weeks)))
    season = SelectField("Season: ", choices=list(zip(seasons, seasons)))
    submit = SubmitField()


class CalculatorForm(FlaskForm):
    point_label = StringField("Point Label", [InputRequired()])
    amnt_pts = IntegerField("Amount of Values", [InputRequired()])
    position = SelectField(
        "Position", [InputRequired()], choices=list(zip(positions, positions))
    )
    season = SelectField(
        "Season", [InputRequired()], choices=list(zip(seasons, seasons))
    )
    week = SelectField("Week", [InputRequired()], choices=list(zip(weeks, weeks)))
    submit = SubmitField()

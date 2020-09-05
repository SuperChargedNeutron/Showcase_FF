from .database import player_coll
import datetime
from flask_wtf import FlaskForm
from wtforms import (
    Form,
    StringField,
    IntegerField,
    SelectField,
    SubmitField,
)
from wtforms.validators import InputRequired, DataRequired

seasons = [str(x) for x in player_coll.find({}).distinct("season")]
positions = ["QB", "RB", "WR", "TE", "DST"]
weeks = [str(i) for i in range(1, 17)]


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

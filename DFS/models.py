from .database import _4f4_Proj
import datetime
from flask_wtf import FlaskForm
from wtforms import Form, StringField, BooleanField, IntegerField, SelectField, SubmitField
from wtforms.validators import InputRequired, DataRequired

seasons = [str(x) for x in _4f4_Proj.find({}).distinct('Season')]
positions = ['QB', 'RB', 'WR', 'TE', 'DST']
weeks = [str(i) for i in range(1, 17)]

class CalculatorForm(FlaskForm):
    point_label = StringField('Point Label', [InputRequired()])
    amnt_pts = IntegerField('Amount of Values', [InputRequired()])
    embedded = BooleanField('Embedded')
    position = SelectField('Position', [InputRequired()], choices = list(zip(positions, positions)))
    season = SelectField('Season', [InputRequired()], choices = list(zip(seasons, seasons)))
    week = SelectField('Week',[InputRequired()], choices = list(zip(weeks, weeks)))
    submit = SubmitField()
from flask import (
    render_template,
    redirect,
    request,
    url_for,
    jsonify
)
from . import app 
from .func import get_raw_data, position_names, player_query, stack_app_query_position
from .database import (db,
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
    ETR_Ceil
)
from .models import CalculatorForm
import urllib.parse

app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = 'you-will-never-guess'

@app.route('/')
def root():
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/<pos>_Dash')
def qb_dash(pos):
    return render_template('dashboard_temp.html', position=pos)

@app.route('/<pos>_data')
def qb_data(pos):

    players =  position_names(pos, db)
    data = [player_query(player, db) for player in players]

    return jsonify(data)

@app.route('/stack_app')
def stack_app():
    return render_template('stack_app.html')

@app.route('/stack_app_data')
def stack_app_data():
    names = {x: stack_app_query_position(x, SS_Data) for x in ['QB', 'WR', 'TE', 'RB', 'DST']}
    teams = [x for x in TeamBuilder.find({}, {'_id':False})]
    data = {
        'names' : names,
        'teams' : teams
        }
    return jsonify(data)

@app.route('/<team_name>/<qb>/<rb1>/<rb2>/<wr1>/<wr2>/<wr3>/<te>/<dst>/<flex>')
def save_new_team(team_name, qb, rb1, rb2, wr1, wr2, wr3, te, dst, flex):
    team = {
        'name' : ' '.join(team_name.split('-')),
        'QB' : ' '.join(qb.split('-')),
        'RBs' : [' '.join(x.split('-')) for x in [rb1, rb2]],
        'WRs' : [' '.join(x.split('-')) for x in[wr1, wr2, wr3]],
        'TE' : ' '.join(te.split('-')),
        'DST' : ' '.join(dst.split('-')),
        'flex' : ' '.join(flex.split('-'))
        }

    TeamBuilder.insert_one(team)

    return redirect('/stack_app')
    
@app.route('/football_calculator_settings', methods=["GET", "POST"])
def calculator_settings():
    form = CalculatorForm(request.form)
    if  form.validate():
        return redirect(urllib.parse.quote(f'/calculator/{form.point_label.data}/{form.amnt_pts.data}/{form.embedded.data}/{form.position.data}/{form.season.data}/{form.week.data}'))
    
    return render_template('calc_settings_jinja.html', form=form)

@app.route('/calculator/<string:label>/<int:amnt>/<embd>/<position>/<season>/<week>')
def football_calculator(label, amnt, embd, position, season, week):
    print('hi')
    return render_template('football_calc.html', label=label, amnt=amnt, embd=embd, position=position, season=season, week=week)
    


@app.route('/team&points_manager')
def teampointmanager():
    return jsonify({'teams and data points' : 'created will be able to be deleted from here'})

@app.route('/saber_sim_raw')
def saber_sim_raw():

    name = 'Saber Sim Data'
    ss_data = get_raw_data(SS_Data)
    headers = list(ss_data[0].keys())
    
    return render_template('raw_data_temp.html', name=name, data=ss_data, headers=headers)



@app.route('/4f4proj')
def _4f4proj():
    name = '4for4 Projection Data'
    _4f4_proj_data =  get_raw_data(_4f4_Proj)
    headers = list(_4f4_proj_data[0].keys())

    return render_template('raw_data_temp.html', name=name, data=_4f4_proj_data, headers=headers)

@app.route('/4f4ceil')
def _4f4ceil():
    name = '4for4 Ceiling Data'
    _4f4_ceil_data =  get_raw_data(_4f4_Ceil)
    headers = list(_4f4_ceil_data[0].keys())

    return render_template('raw_data_temp.html', name=name, data=_4f4_ceil_data, headers=headers)
    
@app.route('/4f4_WR_cb')
def _4f4wrcb():
    name = '4for4 WR cb?'
    _4f4_wrcb_data = get_raw_data(_4f4_WR_cb)
    headers = list(_4f4_wrcb_data[0].keys())

    return render_template('raw_data_temp.html', name=name, data=_4f4_wrcb_data, headers=headers)

@app.route('/4f4_redzone')
def _4f4RedZ():
    name = '4for4 Redzone Data'
    _4f4_redz_data = get_raw_data(_4f4_RedZ)
    headers = list(_4f4_redz_data[0].keys())

    return render_template('raw_data_temp.html', name=name, data=_4f4_redz_data, headers=headers)

@app.route('/4f4_WRfp')
def _4f4wrfp():
    name = '4for4 WR Fantasy Points'
    _4f4_WRfp_data = get_raw_data(_4f4_WR_fp)
    headers = list(_4f4_WRfp_data[0].keys())

    return render_template('raw_data_temp.html', name=name, data=_4f4_WRfp_data, headers=headers)

@app.route('/4f4_RBfp')
def _4f4rbfp():
    name = '4for4 RB Fantasy Points'
    _4f4_rbfp_data = get_raw_data(_4f4_RB_fp)
    headers = list(_4f4_rbfp_data[0].keys())

    return render_template('raw_data_temp.html', name=name, data=_4f4_rbfp_data, headers=headers)

@app.route('/4f4_rbtar')
def _4f4rbtar():
    name = '4for4 RB Target Data'
    _4f4_rbtar_data = get_raw_data(_4f4_RB_tar)
    headers = list(_4f4_rbtar_data[0].keys())
    
    return render_template('raw_data_temp.html', name=name, data=_4f4_rbtar_data, headers=headers)
    
@app.route('/airy_wr')
def airywr():
    name = 'AirY WR Data'
    airywr_data = get_raw_data(airy_WR)
    headers = list(airywr_data[0].keys())

    return render_template('raw_data_temp.html', name=name, data=airywr_data, headers=headers)

@app.route('/airy_te')
def airyte():
    name='AirY TE Data'
    airyte_data = get_raw_data(airy_TE)
    headers = list(airyte_data[0].keys())

    return render_template('raw_data_temp.html', name=name, data=airyte_data, headers=headers)

@app.route('/etr_ceil')
def etrceil():
    name = 'ETR Ceiling Data'
    etrceil_data = get_raw_data(ETR_Ceil)
    headers = list(etrceil_data[0].keys())

    return render_template('raw_data_temp.html', name=name, data=etrceil_data, headers=headers)

##when querying with mongo make sure i define
#  specific columns returned to not mess with JS DtaTables
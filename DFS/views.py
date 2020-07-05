from flask import (
    render_template,
    redirect,
    url_for,
    jsonify
)
from . import app 
from .func import get_raw_data
from .database import (db,
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

@app.route('/')
def root():
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/<table>')
def raw_data(table):
    name = 'Saber Sim Data'
    ss_data = get_raw_data(SS_Data)
    headers = list(ss_data[0].keys())

    return render_template('raw_data_temp.html', name=name, data=ss_data, headers=headers)

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
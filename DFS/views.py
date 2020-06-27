from flask import (
    render_template,
    redirect,
    url_for,
    jsonify
)
from . import app 

@app.route('/')
def root():
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('index.html')


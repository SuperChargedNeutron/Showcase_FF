import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_cors import CORS

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, static_url_path="/static", instance_relative_config=True)

    Bootstrap(app)
    CORS(app)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    return app

app = create_app()

from . import views

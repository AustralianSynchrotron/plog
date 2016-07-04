from flask import Flask
from flask_bootstrap import Bootstrap
import flask_bootstrap
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

flask_bootstrap.StaticCDN(static_endpoint='/static')

Bootstrap(app)

import plog.config
import plog.views


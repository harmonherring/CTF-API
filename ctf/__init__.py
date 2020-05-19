"""CTF - __init__.py

Contains the globally-required objects for the API to function.
Loads blueprints to their respective routes.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPTokenAuth
from flask_cors import CORS

import config

app = Flask(__name__)
app.config.from_object(config)
CORS(app)
db = SQLAlchemy(app)
auth = HTTPTokenAuth(scheme='Bearer')

# pylint: disable=wrong-import-position
from ctf.routes import categories, difficulties, challenges, tags, solved, flags, hints, \
    used_hints, user
# pylint: enable=wrong-import-position

app.register_blueprint(categories, url_prefix='/categories')
app.register_blueprint(difficulties, url_prefix='/difficulties')
app.register_blueprint(challenges, url_prefix='/challenges')
app.register_blueprint(tags, url_prefix='/challenges')
app.register_blueprint(solved, url_prefix='/challenges')
app.register_blueprint(flags)
app.register_blueprint(hints)
app.register_blueprint(used_hints)
app.register_blueprint(user, url_prefix='/user')

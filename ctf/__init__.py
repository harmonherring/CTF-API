"""CTF - __init__.py

Contains the globally-required objects for the API to function.
Loads blueprints to their respective routes.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask_httpauth import HTTPTokenAuth
from flask_cors import CORS
import csh_ldap

import config

app = Flask(__name__)
app.config.from_object(config)
CORS(app)
db = SQLAlchemy(app)
auth = HTTPTokenAuth(scheme='Bearer')
_ldap = csh_ldap.CSHLDAP(app.config["LDAP_DN"], app.config["LDAP_PW"])

# pylint: disable=wrong-import-position
from ctf.routes import categories, difficulties, challenges, tags, solved, flags, hints, used_hints
# pylint: enable=wrong-import-position

app.register_blueprint(categories, url_prefix='/categories')
app.register_blueprint(difficulties, url_prefix='/difficulties')
app.register_blueprint(challenges, url_prefix='/challenges')
app.register_blueprint(tags, url_prefix='/challenges')
app.register_blueprint(solved, url_prefix='/challenges')
app.register_blueprint(flags)
app.register_blueprint(hints)
app.register_blueprint(used_hints)

"""CTF - __init__.py

Contains the globally-required objects for the API to function.
Loads blueprints to their respective routes.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
import csh_ldap

import config

app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)
auth = OIDCAuthentication(
    app,
    issuer=app.config['OIDC_ISSUER'],
    client_registration_info=app.config['OIDC_CLIENT_CONFIG'])
_ldap = csh_ldap.CSHLDAP(app.config["LDAP_DN"], app.config["LDAP_PW"])

# pylint: disable=wrong-import-position
from ctf.routes import categories
# pylint: enable=wrong-import-position

app.register_blueprint(categories, url_prefix='/categories')

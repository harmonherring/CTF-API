from os import environ, path, getcwd
import requests

APP_NAME = environ.get('CTF_APP_NAME', "CTF")
HOST_NAME = environ.get('CTF_HOST_NAME', "localhost:5000")
SERVER_NAME = environ.get('CTF_SERVER_NAME', "localhost:5000")
DEBUG = environ.get('CTF_DEBUG', False)
IP = environ.get('CTF_IP', "0.0.0.0")
PORT = environ.get('CTF_PORT', 8080)
SECRET_KEY = environ.get("CTF_SECRET_KEY", None)

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_POOL_RECYCLE = 500
SQLALCHEMY_DATABASE_URI = environ.get('CTF_DATABASE_URI', 'sqlite:////{}'.format(path.join(getcwd(), 'data.db')))

# OpenID Connect SSO config
OIDC_PUBLIC_KEY = \
    b"-----BEGIN PUBLIC KEY-----\n" + \
    bytes(requests.get("https://sso.csh.rit.edu/auth/realms/csh").json()['public_key'], 'UTF-8') + \
    b"\n-----END PUBLIC KEY-----"
OIDC_USERINFO_ENDPOINT = "https://sso.csh.rit.edu/auth/realms/csh/protocol/openid-connect/userinfo"
OIDC_ISSUER = environ.get('CTF_OIDC_ISSUER', 'https://sso.csh.rit.edu/auth/realms/csh')
OIDC_CLIENT_CONFIG = {
    'client_id': environ.get('CTF_OIDC_CLIENT_ID', 'ctf'),
    'client_secret': environ.get('CTF_OIDC_CLIENT_SECRET', ''),
    'post_logout_redirect_uris': [environ.get('CTF_OIDC_LOGOUT_REDIRECT_URI', 'https://quotefault-api.csh.rit.edu/logout')]
}

# LDAP config
LDAP_DN = environ.get('CTF_LDAP_DN', "")
LDAP_PW = environ.get('CTF_LDAP_PW', "")

# CORS config
CORS_SUPPORTS_CREDENTIALS = True

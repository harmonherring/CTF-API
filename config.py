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
SQLALCHEMY_DATABASE_URI = environ.get('CTF_DATABASE_URI', 'sqlite:////{}'.format(
    path.join(getcwd(), 'data.db')))

# OpenID Connect SSO config
OIDC_PUBLIC_KEY = \
    b"-----BEGIN PUBLIC KEY-----\n" + \
    bytes(requests.get("https://sso.csh.rit.edu/auth/realms/csh").json()['public_key'], 'UTF-8') + \
    b"\n-----END PUBLIC KEY-----"
OIDC_USERINFO_ENDPOINT = "https://sso.csh.rit.edu/auth/realms/csh/protocol/openid-connect/userinfo"

# CORS config
CORS_SUPPORTS_CREDENTIALS = True

# File config
UPLOAD_PATH = "./uploads"
ALLOWED_MIME_TYPES = ["application/zip", "application/gzip", "application/x-tar",
                      "application/x-7z-compressed"]

# S3 Configuration
S3_ACCESS_KEY_ID = environ.get("CTF_S3_ACCESS_KEY_ID", None)
S3_SECRET_ACCESS_KEY = environ.get("CTF_S3_SECRET_ACCESS_KEY", None)
S3_ENDPOINT_URL = environ.get("CTF_S3_ENDPOINT_URL", None)
S3_BUCKET = environ.get("CTF_S3_BUCKET", None)

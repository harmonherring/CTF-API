from os import environ, path, getcwd

APP_NAME = environ.get('CTF_APP_NAME', "CTF")
HOST_NAME = environ.get('CTF_HOST_NAME', "localhost:5000")
SERVER_NAME = environ.get('CTF_SERVER_NAME', "localhost:5000")
DEBUG = environ.get('CTF_DEBUG', False)
IP = environ.get('CTF_IP', "0.0.0.0")
PORT = environ.get('CTF_PORT', 8080)

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = environ.get('CTF_DATABASE_URI', 'sqlite:////{}'.format(path.join(getcwd(), 'data.db')))

""" CTF - user.py

Contains a route that returns the currently authenticated user's information
"""
from flask import Blueprint, jsonify

from ctf import auth
from ctf.utils import get_userinfo

user_bp = Blueprint('user', __name__)


@user_bp.route('', methods=['GET'])
@auth.login_required
def user():
    """
    Retrieves the userinfo for the currently authenticate user
    """
    userinfo = get_userinfo(auth.current_user())
    if "ctf" in userinfo['groups'] or "rtp" in userinfo['groups']:
        userinfo['admin'] = True
    else:
        userinfo['admin'] = False
    return jsonify(userinfo), 200

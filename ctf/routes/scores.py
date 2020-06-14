""" CTF - scores.py

This module contains the routes that retrieve score for users
"""

from flask import Blueprint, jsonify

from ctf import auth
from ctf.models import Solved, UsedHint
from ctf.utils import get_user_score

score_bp = Blueprint('scores', __name__)


@score_bp.route('', methods=['GET'])
@auth.login_required
def get_all_scores():
    """
    Gets the score for all users
    """
    all_scores = {}
    for solved in Solved.query.all():
        all_scores[solved.username] = all_scores.get(solved.username, 0) + solved.flag.point_value
    for used_hint in UsedHint.query.all():
        all_scores[used_hint.username] = all_scores.get(used_hint.username, 0) - used_hint.hint.cost
    return jsonify(all_scores), 200


@score_bp.route('/<username>', methods=['GET'])
@auth.login_required
def get_users_score(username: str):
    """
    Gets the score of a particular user
    :param username: Username to retrieve the score of
    """
    return jsonify({username: get_user_score(username)}), 200

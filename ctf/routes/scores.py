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

    :TODO: Use SQL queries so this is more efficient
    """
    all_scores = {}
    for solved in Solved.query.all():
        if solved.username not in all_scores:
            all_scores[solved.username] = {
                'score': 0,
                'solved_flags': 0
            }
        all_scores[solved.username]['score'] = all_scores[solved.username]['score'] + \
            solved.flag.point_value
        all_scores[solved.username]['solved_flags'] += 1
    for used_hint in UsedHint.query.all():
        all_scores[used_hint.username]['score'] = all_scores[used_hint.username]['score'] - \
            used_hint.flag.point_value
    return jsonify(all_scores), 200


@score_bp.route('/<username>', methods=['GET'])
@auth.login_required
def get_users_score(username: str):
    """
    Gets the score of a particular user
    :param username: Username to retrieve the score of
    """
    score, solved_flags = get_user_score(username)
    return jsonify({username: {
        'score': score,
        'solved_flags': solved_flags
    }}), 200

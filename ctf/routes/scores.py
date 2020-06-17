""" CTF - scores.py

This module contains the routes that retrieve score for users
"""
from datetime import datetime

from flask import Blueprint, jsonify, request

from ctf import auth
from ctf.models import Solved, UsedHint
from ctf.utils import get_user_score

score_bp = Blueprint('scores', __name__)


@score_bp.route('', methods=['GET'])
@auth.login_required
def get_all_scores():
    """
    Gets the score for all users

    URL Parameters:
        :url_param after: Request scores after this date
        :url_param before: Request scores before this date
    :TODO: Use SQL queries so this is more efficient
    """
    try:
        after = datetime.strptime(request.args.get('after', ''), "%Y-%m-%d%H:%M:%S")
    except ValueError or TypeError:
        return jsonify({
            'status': "error",
            'message': "Date should be formatted as %Y-%m-%d%H:%M:%S"
        }), 400
    try:
        before = datetime.strptime(request.args.get('before', ''), "%Y-%m-%d%H:%M:%S")
    except ValueError or TypeError:
        return jsonify({
            'status': "error",
            'message': "Date should be formatted as %Y-%m-%d%H:%M:%S"
        }), 400

    solved_query = Solved.query
    hint_query = UsedHint.query
    if after:
        solved_query = solved_query.filter(Solved.ts >= after)
        hint_query = hint_query.filter(UsedHint.ts >= after)
    if before:
        solved_query = solved_query.filter(Solved.ts <= before)
        hint_query = hint_query.filter(UsedHint.ts <= before)

    all_scores = {}
    for solved in solved_query.all():
        if solved.username not in all_scores:
            all_scores[solved.username] = {
                'score': 0,
                'solved_flags': 0
            }
        all_scores[solved.username]['score'] = all_scores[solved.username]['score'] + \
            solved.flag.point_value
        all_scores[solved.username]['solved_flags'] += 1
    for used_hint in hint_query.all():
        all_scores[used_hint.username]['score'] = all_scores[used_hint.username]['score'] - \
            used_hint.hint.flag.point_value
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

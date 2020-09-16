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
        :url_param limit: Limit the number of user scores that are requested
    :TODO: Use SQL queries so this is more efficient
    """
    limit = int(request.args.get('limit'))
    after = request.args.get('after')
    before = request.args.get('before')

    if after:
        try:
            after = datetime.strptime(request.args.get('after', ''), "%Y-%m-%d%H:%M:%S")
        except:
            return jsonify({
                'status': "error",
                'message': "Date should be formatted as %Y-%m-%d%H:%M:%S"
            }), 400
    if before:
        try:
            before = datetime.strptime(request.args.get('before', ''), "%Y-%m-%d%H:%M:%S")
        except:
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
            used_hint.hint.cost

    if limit and 0 < limit < len(all_scores):
        # Get and sort all scores from dictionary
        scores = [x['score'] for x in all_scores.values()]
        scores.sort()
        score_threshold = scores[limit-1]
        for i in list(all_scores.keys()):
            if all_scores[i]['score'] < score_threshold:
                del all_scores[i]
        if len(all_scores) > limit:
            # This occurs if the limit and limit+1 person have the same score
            most_flags = max([x['solved_flags'] for x in all_scores.values() if x['score'] ==
                              score_threshold])
            # Delete those who are at the threshold and have fewer than the maximum number of
            # flags at the threshold
            for i in list(all_scores.keys()):
                if all_scores[i]['score'] == score_threshold and \
                        all_scores[i]['solved_flags'] < most_flags:
                    del all_scores[i]
            if len(all_scores) > limit:
                # This will occur if two people have the same score and number of flags
                # Delete them at random
                for i in list(all_scores.keys()):
                    if all_scores[i]['score'] == score_threshold and \
                            all_scores[i]['solved_flags'] == most_flags:
                        del all_scores[i]
                        break

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

""" CTF - solved.py

These API routes are poorly named. They keep a record of who has solved which flags.
"""

from flask import Blueprint, jsonify, request

from ctf import auth
from ctf.models import Solved, Flag, Challenge
from ctf.utils import TSAPreCheck

solved_bp = Blueprint('solved', __name__)


@solved_bp.route('/<int:challenge_id>/solved', methods=['GET'])
@auth.oidc_auth
def solved_flags(challenge_id: int):
    """
    Operations pertaining to the solution of flags

    :GET: Get a list of the users who have solved each flag belonging to the specified challenge
    """
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    precheck = TSAPreCheck().ensure_existence((challenge, Challenge))
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    flags = Flag.query.filter_by(challenge_id=challenge_id).all()
    response = dict()

    for flag in flags:
        solved = Solved.query.filter_by(flag_id=flag.id).all()
        response[flag.id] = [solution.username for solution in solved]

    if request.method == 'GET':
        return jsonify(response), 200


@solved_bp.route('/<int:challenge_id>/solved', methods=['POST'])
@auth.oidc_auth
def solve_flag(challenge_id: int):
    """
    Operations pertaining to the solved relations on a challenge (but really a flag).

    :param challenge_id: The challenge that a solution is being attempted on

    :POST: Attempt solution of all flags associated with this challenge
    """
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    precheck = TSAPreCheck().ensure_existence((challenge, Challenge)).has_json_args("flag")
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    if request.method == 'POST':
        data = request.get_json()
        flag_attempt = data['flag']
        flags = Flag.query.filter_by(challenge_id=challenge_id).all()
        current_user = precheck.get_current_user()
        if precheck.error_code:
            return jsonify(precheck.message), precheck.error_code

        for flag in flags:
            if flag.flag == flag_attempt:
                check_solved = Solved.query.filter_by(flag_id=flag.id,
                                                      username=current_user).first()
                precheck.ensure_nonexistence((check_solved, Solved))
                if precheck.error_code:
                    return jsonify(precheck.message), precheck.error_code

                Solved.create(flag.id, current_user)
                return jsonify(challenge.to_dict()), 201
        return jsonify({
            'status': "error",
            'message': "Incorrect flag"
        }), 400

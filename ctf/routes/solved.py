""" CTF - solved.py

These API routes are poorly named. They keep a record of who has solved which flags.
"""

from flask import Blueprint, jsonify, request

from ctf import auth
from ctf.models import Solved, Flag, Challenge
from ctf.utils import TSAPreCheck, has_json_args
from ctf.constants import collision, not_found

solved_bp = Blueprint('solved', __name__)


@solved_bp.route('/<int:challenge_id>/solved', methods=['GET'])
@auth.login_required
def solved_flags(challenge_id: int):
    """
    Operations pertaining to the solution of flags

    :GET: Get a list of the users who have solved each flag belonging to the specified challenge
    """
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        return not_found()

    flags = Flag.query.filter_by(challenge_id=challenge_id).all()
    response = dict()

    for flag in flags:
        solved = Solved.query.filter_by(flag_id=flag.id).all()
        response[flag.id] = [solution.username for solution in solved]

    return jsonify(response), 200


@solved_bp.route('/<int:challenge_id>/solved', methods=['POST'])
@auth.login_required
@has_json_args("flag")
def solve_flag(challenge_id: int):
    """
    Operations pertaining to the solved relations on a challenge (but really a flag).

    :param challenge_id: The challenge that a solution is being attempted on

    :POST: Attempt solution of all flags associated with this challenge
    """
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    precheck = TSAPreCheck()
    if not challenge:
        return not_found()

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
            if check_solved:
                return collision()

            Solved.create(flag.id, current_user)
            return jsonify(challenge.to_dict()), 201
    return jsonify({
        'status': "error",
        'message': "Incorrect flag"
    }), 400

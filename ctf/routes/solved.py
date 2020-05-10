""" CTF - solved.py

These API routes are poorly named. They keep a record of who has solved which flags.
"""

from flask import Blueprint, jsonify, request

from ctf import auth
from ctf.models import Solved, Flag, Challenge
from ctf.utils import TSAPreCheck

solved_bp = Blueprint('solved', __name__)


@solved_bp.route('/<int:challenge_id>/flags/<int:flag_id>/solved', methods=['GET'])
@auth.oidc_auth
def solved_flags(challenge_id: int, flag_id: int):
    """
    Operations pertaining to the solution of flags

    :GET: Get a list of the users who have solved this flag
    """
    flag = Flag.query.filter_by(id=flag_id).first()
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    precheck = TSAPreCheck().ensure_existence((challenge, Challenge), (flag, Flag))
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    if request.method == 'GET':
        return jsonify([solved.to_dict()['username'] for solved in Solved.query.filter_by(
            flag_id=flag_id).all()]), 200


@solved_bp.route('/<int:challenge_id>/flags/<int:flag_id>/solved', methods=['POST'])
@auth.oidc_auth
def solve_flag(challenge_id: int, flag_id: int):
    """
    Operations pertaining to a single flag solution. This is primarily attempting a flag solution.
    This is a bit wonky, because I'd like for someone to be able to hit the Challenge object with a
    flag key and then have the API check all keys associated with that Challenge. It's 2am
    though, and I can't find a way for that to fit in with the URL verbiage, so...the flag_id
    key is pretty much just ignored.

    :param challenge_id: The challenge that a solution is being attempted on
    :param flag_id: The flag that's being solved. This value is ignored

    :POST: Attempt solution of all flags associated with this challenge
    """
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    _flag = Flag.query.filter_by(id=flag_id).first()
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

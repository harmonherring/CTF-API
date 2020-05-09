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

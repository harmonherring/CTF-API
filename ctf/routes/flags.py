""" CTF - flags.py

Contains routes pertaining to the retrieval and creation of flags
"""

from flask import Blueprint, request, jsonify

from ctf import auth
from ctf.models import Flag, Challenge, Solved
from ctf.utils import TSAPreCheck, delete_flag

flags_bp = Blueprint('flags', __name__)


@flags_bp.route('/challenges/<int:challenge_id>/flags', methods=['GET'])
@auth.login_required
def all_flags(challenge_id: int):
    """
    Operations relating to flags

    :GET: Retrieves a list of flags associated with a challenge. The flag value is omitted if the
        person fetching hasn't yet solved the flag
    :POST: Creates a flag associated with a challenge
    """
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    precheck = TSAPreCheck().ensure_existence((challenge, Challenge))
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    # If the person hasn't solved the flag, the flag data should be omitted.
    current_user = precheck.get_current_user()
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code
    flags = [flag.to_dict() for flag in Flag.query.filter_by(challenge_id=challenge_id).all()]
    for flag in flags:
        if not Solved.query.filter_by(username=current_user, flag_id=flag['id']).first():
            del flag['flag']
    return jsonify(flags), 200


@flags_bp.route('/challenges/<int:challenge_id>/flags', methods=['POST'])
@auth.login_required
def add_flag(challenge_id: int):
    """
    Create a flag given parameters in application/json body
    """
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    precheck = TSAPreCheck().ensure_existence((challenge, Challenge))
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    data = request.get_json()
    precheck_flag = Flag.query.filter_by(challenge_id=challenge_id, flag=data.get('flag') if
                                         data else None).first()
    precheck.is_authorized(challenge.submitter).has_json_args("point_value", "flag") \
        .ensure_nonexistence((precheck_flag, Flag))
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    new_flag = Flag.create(data['point_value'], data['flag'], challenge_id)
    Solved.create(new_flag['id'], challenge.submitter)
    return jsonify(new_flag), 201


@flags_bp.route('/<int:challenge_id>/flags/<int:flag_id>', methods=['DELETE'])
@flags_bp.route('/flags/<int:flag_id>', methods=['DELETE'])
@auth.login_required(role=['ctf', 'rtp'])
def single_flag(challenge_id: int = 0, flag_id: int = 0):
    # pylint: disable=unused-argument
    """
    Deletes the flag specified
    """
    flag = Flag.query.filter_by(id=flag_id).first()
    precheck = TSAPreCheck().ensure_existence((flag, Flag))\
        .is_authorized(flag.challenge.submitter if flag else None)
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    if request.method == 'DELETE':
        delete_flag(flag.id)
        return '', 204

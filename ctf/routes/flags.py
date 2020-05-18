""" CTF - flags.py

Contains routes pertaining to the retrieval and creation of flags
"""

from flask import Blueprint, request, jsonify

from ctf import auth
from ctf.models import Flag, Challenge, Solved
from ctf.utils import delete_flag, has_json_args, expose_userinfo, is_ctf_admin
from ctf.constants import not_found, collision, not_authorized, no_username

flags_bp = Blueprint('flags', __name__)


@flags_bp.route('/challenges/<int:challenge_id>/flags', methods=['GET'])
@auth.login_required
@expose_userinfo
def all_flags(challenge_id: int, **kwargs):
    """
    Operations relating to flags

    :GET: Retrieves a list of flags associated with a challenge. The flag value is omitted if the
        person fetching hasn't yet solved the flag
    :POST: Creates a flag associated with a challenge
    """
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        return not_found()

    # If the person hasn't solved the flag, the flag data should be omitted.
    current_username = kwargs['userinfo'].get('preferred_username')
    if not current_username:
        return no_username()

    flags = [flag.to_dict() for flag in Flag.query.filter_by(challenge_id=challenge_id).all()]
    for flag in flags:
        if not Solved.query.filter_by(username=current_username, flag_id=flag['id']).first():
            del flag['flag']
    return jsonify(flags), 200


@flags_bp.route('/challenges/<int:challenge_id>/flags', methods=['POST'])
@auth.login_required
@has_json_args("point_value", "flag")
@expose_userinfo
def add_flag(challenge_id: int, **kwargs):
    """
    Create a flag given parameters in application/json body
    """
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        return not_found()

    data = request.get_json()
    flag_exists = Flag.query.filter_by(challenge_id=challenge_id, flag=data['flag']).first()
    if flag_exists:
        return collision()

    current_username = kwargs['userinfo'].get('preferred_username')
    if not current_username:
        return no_username()
    groups = kwargs['userinfo'].get('groups')
    if current_username != challenge.submitter and not is_ctf_admin(groups):
        return not_authorized()

    new_flag = Flag.create(data['point_value'], data['flag'], challenge_id)
    Solved.create(new_flag['id'], challenge.submitter)
    return jsonify(new_flag), 201


@flags_bp.route('/<int:challenge_id>/flags/<int:flag_id>', methods=['DELETE'])
@flags_bp.route('/flags/<int:flag_id>', methods=['DELETE'])
@auth.login_required
@expose_userinfo
def single_flag(challenge_id: int = 0, flag_id: int = 0, **kwargs):
    # pylint: disable=unused-argument
    """
    Deletes the flag specified
    """
    flag = Flag.query.filter_by(id=flag_id).first()
    if not flag:
        return not_found()

    current_username = kwargs['userinfo'].get('preferred_username')
    if not current_username:
        return no_username()
    groups = kwargs['userinfo'].get('groups')
    if current_username != flag.challenge.submitter and not is_ctf_admin(groups):
        return not_authorized()

    delete_flag(flag.id)
    return jsonify({
        'status': "success"
    }), 200

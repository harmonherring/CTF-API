""" CTF - hints.py

Contains routes relating to hints
"""

from flask import Blueprint, request, jsonify

from ctf import auth
from ctf.models import Hint, Flag, UsedHint
from ctf.utils import delete_hint, has_json_args, expose_userinfo
from ctf.constants import not_found, not_authorized, no_username

hints_bp = Blueprint('hints', __name__)


@hints_bp.route('/challenges/<int:challenge_id>/flags/<int:flag_id>/hints', methods=['GET'])
@hints_bp.route('/flags/<int:flag_id>/hints', methods=['GET'])
@auth.login_required
@expose_userinfo
def all_hints(challenge_id: int, flag_id: int, **kwargs):
    # pylint: disable=unused-argument
    """
    Operations relating to the hints objects

    :GET: Get all hints associated with the specified flag and challenge
    """
    flag = Flag.query.filter_by(id=flag_id).first()
    if not flag:
        return not_found()

    current_username = kwargs['userinfo'].get('preferred_username')
    if not current_username:
        return no_username()

    # Delete a hint's data if a user hasn't unlocked it
    hints = [hint.to_dict() for hint in Hint.query.filter_by(flag_id=flag_id).all()]
    for hint in hints:
        if not UsedHint.query.filter_by(hint_id=hint['id'], username=current_username).first():
            del hint['hint']
    return jsonify(hints), 200


@hints_bp.route('/challenges/<int:challenge_id>/flags/<int:flag_id>/hints', methods=['POST'])
@hints_bp.route('/flags/<int:flag_id>/hints', methods=['POST'])
@auth.login_required
@has_json_args("cost", "hint")
@expose_userinfo
def create_hint(challenge_id: int, flag_id: int, **kwargs):
    # pylint: disable=unused-argument
    """
    Creates a hint given parameters in the application/json body
    """
    flag = Flag.query.filter_by(id=flag_id).first()
    if not flag:
        return not_found()

    current_username = kwargs['userinfo'].get('preferred_username')
    if not current_username:
        return no_username()

    data = request.get_json()
    new_hint = Hint.create(data['cost'], data['hint'], flag_id)

    # TODO: Remove this, change the hint return functions to reveal hint if current_user is creator
    UsedHint.create(new_hint['id'], current_username)
    return jsonify(new_hint), 201


@hints_bp.route('/challenges/<int:challenge_id>/flags/<int:flag_id>/hints/<int:hint_id>',
                methods=['DELETE'])
@hints_bp.route('/flags/<int:flag_id>/hints/<int:hint_id>', methods=['DELETE'])
@hints_bp.route('/hints/<int:hint_id>', methods=['DELETE'])
@auth.login_required
@expose_userinfo
def one_hint(challenge_id: int = 0, flag_id: int = 0, hint_id: int = 0, **kwargs):
    # pylint: disable=unused-argument
    """
    Deletes the specified hint
    """
    hint = Hint.query.filter_by(id=hint_id).first()

    if not hint:
        return not_found()

    current_username = kwargs['userinfo'].get('preferred_username')
    if not current_username:
        return no_username()
    groups = kwargs['userinfo'].get('groups')
    if current_username != hint.flag.challenge.submitter and "rtp" not in groups and "ctf" not in\
            groups:
        return not_authorized()

    delete_hint(hint_id)
    return '', 204

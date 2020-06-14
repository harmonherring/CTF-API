""" CTF - hints.py

Contains routes relating to hints
"""

from flask import Blueprint, request, jsonify

from ctf import auth
from ctf.models import Hint, Flag, UsedHint, Solved
from ctf.utils import delete_hint, has_json_args, expose_userinfo, is_ctf_admin, get_user_score
from ctf.constants import not_found, not_authorized, no_username, collision

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
    is_flag_creator = flag.challenge.submitter == current_username
    for hint in hints:
        if not is_flag_creator and \
           not UsedHint.query.filter_by(hint_id=hint['id'], username=current_username).first():
            del hint['hint']
    return jsonify(hints), 200


@hints_bp.route('/challenges/<int:challenge_id>/flags/<int:flag_id>/hints', methods=['POST'])
@hints_bp.route('/flags/<int:flag_id>/hints', methods=['POST'])
@auth.login_required
@has_json_args("cost", "hint")
@expose_userinfo
def create_hint(challenge_id: int = 0, flag_id: int = 0, **kwargs):
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

    return jsonify(new_hint), 201


@hints_bp.route('/challenges/<int:challenge_id>/flags/<int:flag_id>/hints/<int:hint_id>',
                methods=['POST'])
@hints_bp.route('/flags/<int:flag_id>/hints/<int:hint_id>', methods=['POST'])
@hints_bp.route('/hints/<int:hint_id>', methods=['POST'])
@auth.login_required
@expose_userinfo
def purchase_hint(challenge_id: int = 0, flag_id: int = 0, hint_id: int = 0, **kwargs):
    # pylint: disable=unused-argument
    """
    Operations relating to used hints

    :POST: Allow a user to pay for a hint
    """
    hint = Hint.query.filter_by(id=hint_id).first()
    if not hint:
        return not_found()

    current_username = kwargs['userinfo'].get('preferred_username')
    if not current_username:
        return no_username()

    # Check that the relation doesn't already exist
    used_hints_check = UsedHint.query.filter_by(hint_id=hint_id, username=current_username).first()
    if used_hints_check:
        return collision()

    if current_username == hint.flag.challenge.submitter:
        return jsonify({
            'status': "error",
            'message': "You created this hint!"
        }), 403

    if Solved.query.filter_by(flag_id=hint.flag.id).first():
        return jsonify({
            'status': "error",
            'message': "You already solved the flag associated with this hint!"
        }), 422

    if get_user_score(current_username) - hint.cost < 0:
        return jsonify({
            'status': "error",
            'message': "You don't have enough points to purchase this hint!"
        }), 422

    new_used_hint = UsedHint.create(hint_id, current_username)
    return jsonify(new_used_hint.hint.to_dict()), 201


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
    if current_username != hint.flag.challenge.submitter and not is_ctf_admin(groups):
        return not_authorized()

    delete_hint(hint_id)
    return jsonify({
        'status': "success"
    }), 200

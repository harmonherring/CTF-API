""" CTF - hints.py

Contains routes relating to hints
"""

from flask import Blueprint, request, jsonify

from ctf import auth
from ctf.models import Hint, Flag, UsedHint
from ctf.utils import TSAPreCheck, delete_hint

hints_bp = Blueprint('hints', __name__)


@hints_bp.route('/challenges/<int:challenge_id>/flags/<int:flag_id>/hints', methods=['GET', 'POST'])
@hints_bp.route('/flags/<int:flag_id>/hints', methods=['GET', 'POST'])
@auth.oidc_auth
def all_hints(challenge_id: int, flag_id: int):
    # pylint: disable=unused-argument
    """
    Operations relating to the hints objects

    :param challenge_id: This is probably going to be ignored, because hints are directly
        associated with flags
    :param flag_id: The flag of which we're manipulating hints

    :GET: Get all hints associated with the specified flag and challenge
    :POST: Create a hint for a flag
    """
    flag = Flag.query.filter_by(id=flag_id).first()
    precheck = TSAPreCheck().ensure_existence((flag, Flag))
    current_username = precheck.get_current_user()
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    if request.method == 'GET':
        hints = [hint.to_dict() for hint in Hint.query.filter_by(flag_id=flag_id).all()]
        for hint in hints:
            if not UsedHint.query.filter_by(hint_id=hint['id'], username=current_username).first():
                del hint['hint']
        return jsonify(hints), 200
    elif request.method == 'POST':
        precheck.is_authorized(flag.challenge.submitter).has_json_args("cost", "hint")
        if precheck.error_code:
            return jsonify(precheck.message), precheck.error_code
        data = request.get_json()
        new_hint = Hint.create(data['cost'], data['hint'], flag_id)
        UsedHint.create(new_hint['id'], current_username)
        return jsonify(new_hint), 201


@hints_bp.route('/challenges/<int:challenge_id>/flags/<int:flag_id>/hints/<int:hint_id>',
                methods=['DELETE'])
@hints_bp.route('/flags/<int:flag_id>/hints/<int:hint_id>', methods=['DELETE'])
@hints_bp.route('/hints/<int:hint_id>', methods=['DELETE'])
@auth.oidc_auth
def one_hint(challenge_id: int = 0, flag_id: int = 0, hint_id: int = 0):
    # pylint: disable=unused-argument
    """
    Operations pertaining to one hint

    :DELETE: Deletes the specified hint
    """
    hint = Hint.query.filter_by(id=hint_id).first()

    precheck = TSAPreCheck().ensure_existence((hint, Hint))
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    if request.method == 'DELETE':
        precheck.is_authorized(hint.flag.challenge.submitter)
        if precheck.error_code:
            return jsonify(precheck.message), precheck.error_code

        delete_hint(hint_id)
        return '', 204

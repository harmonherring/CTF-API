""" CTF - used_hints.py

Contains information regarding the used hints relationship
"""

from flask import Blueprint, request, jsonify

from ctf import auth
from ctf.models import UsedHint
from ctf.utils import TSAPreCheck

used_hints_bp = Blueprint('used_hints', __name__)


@used_hints_bp.route('/challenges/<int:challenge_id>/flags/<int:flag_id>/hints/<int:hint_id>/used',
                     methods=['POST'])
@used_hints_bp.route('/flags/<int:flag_id>/hints/<int:hint_id>/used', methods=['POST'])
@used_hints_bp.route('/hints/<int:hint_id>/used', methods=['POST'])
@auth.login_required
def create_hint(challenge_id: int = 0, flag_id: int = 0, hint_id: int = 0):
    # pylint: disable=unused-argument
    """
    Operations relating to used hints

    Good lord I can't believe Flask let me do this with the parameters

    :POST: Allow a user to pay for a hint
    """
    precheck = TSAPreCheck()
    current_user = precheck.get_current_user()
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    if request.method == 'POST':
        # Check that the relation doesn't already exist
        used_hints_check = UsedHint.query.filter_by(hint_id=hint_id, username=current_user).first()
        precheck.ensure_nonexistence((used_hints_check, UsedHint))
        if precheck.error_code:
            return jsonify(precheck.message), precheck.error_code

        # TODO: Check that the user has enough points for the cost
        new_used_hint = UsedHint.create(hint_id, current_user)
        return jsonify(new_used_hint.hint.to_dict()), 201

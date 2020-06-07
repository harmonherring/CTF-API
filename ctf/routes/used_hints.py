""" CTF - used_hints.py

Contains information regarding the used hints relationship
"""

from flask import Blueprint, jsonify

from ctf import auth
from ctf.models import UsedHint, Hint
from ctf.utils import expose_userinfo
from ctf.constants import collision, no_username, not_found

used_hints_bp = Blueprint('used_hints', __name__)


@used_hints_bp.route('/challenges/<int:challenge_id>/flags/<int:flag_id>/hints/<int:hint_id>/used',
                     methods=['POST'])
@used_hints_bp.route('/flags/<int:flag_id>/hints/<int:hint_id>/used', methods=['POST'])
@used_hints_bp.route('/hints/<int:hint_id>/used', methods=['POST'])
@auth.login_required
@expose_userinfo
def create_hint(challenge_id: int = 0, flag_id: int = 0, hint_id: int = 0, **kwargs):
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

    # TODO: Check that the user has enough points for the cost
    new_used_hint = UsedHint.create(hint_id, current_username)
    return jsonify(new_used_hint.hint.to_dict()), 201

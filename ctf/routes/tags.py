""" CTF - tags.py

Contains routes pertaining to the Tags assigned to a Challenge
"""

from flask import Blueprint, jsonify
from sqlalchemy import func

from ctf import auth
from ctf.models import Challenge, ChallengeTag
from ctf.utils import TSAPreCheck
from ctf.constants import not_found, collision


tags_bp = Blueprint("tags", __name__)


@tags_bp.route('/<int:challenge_id>/tags', methods=['GET'])
@auth.login_required
def all_tags(challenge_id: int):
    """
    Operations pertaining to tags

    :GET: Returns a list of all tags for the challenge with 'challenge_id'
    """
    # Ensure challenge exists
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        return not_found()

    return jsonify([tag.to_dict() for tag in challenge.tags]), 200


@tags_bp.route('/<int:challenge_id>/tags/<tag_name>', methods=['POST'])
@auth.login_required
def single_tag(challenge_id: int, tag_name: str):
    """
    Creates a tag
    """
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        return not_found()

    tag = ChallengeTag.query.filter(func.lower(ChallengeTag.tag) == func.lower(tag_name),
                                    ChallengeTag.challenge_id == challenge_id).first()
    if tag:
        return collision()

    precheck = TSAPreCheck().is_authorized(challenge.submitter)
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    new_tag = ChallengeTag.create(challenge_id, tag_name)
    return jsonify(new_tag), 201


@tags_bp.route('/<int:challenge_id>/tags/<tag_name>', methods=['DELETE'])
@auth.login_required
def delete_tag(challenge_id: int, tag_name: str):
    """
    Deletes the specified tag
    """
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        return not_found()

    tag = ChallengeTag.query.filter(func.lower(ChallengeTag.tag) == func.lower(tag_name),
                                    ChallengeTag.challenge_id == challenge_id).first()
    if not tag:
        return not_found()

    precheck = TSAPreCheck().is_authorized(challenge.submitter)
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    tag.delete()
    return '', 204

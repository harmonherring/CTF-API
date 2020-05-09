""" CTF - tags.py

Contains routes pertaining to the Tags assigned to a Challenge
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import func

from ctf import auth
from ctf.models import Challenges, ChallengeTags
from ctf.utils import run_checks


tags_bp = Blueprint("tags", __name__)


@tags_bp.route('/<int:challenge_id>/tags', methods=['GET'])
@auth.oidc_auth
def all_tags(challenge_id: int):
    """
    Operations pertaining to tags

    :GET: Returns a list of all tags for the challenge with 'challenge_id'
    """
    if request.method == 'GET':
        challenge = Challenges.query.filter_by(id=challenge_id).first()
        if not challenge:
            return jsonify({
                'status': "error",
                'message': "Challenge doesn't exist"
            }), 404
        return jsonify([tag.to_dict() for tag in challenge.tags]), 200


@tags_bp.route('/<int:challenge_id>/tags/<tag_name>', methods=['POST', 'DELETE'])
@auth.oidc_auth
def single_tag(challenge_id: int, tag_name: str):
    """
    Operations pertaining to a single tag

    :POST: Create a tag with 'tag_name' and 'challenge_id'
    :DELETE: Delete a tag with 'tag_name' and 'challenge_id'
    """
    if request.method == 'POST':
        challenge = Challenges.query.filter_by(id=challenge_id).first()
        if not challenge:
            return jsonify({
                'status': "error",
                'message': "Challenge doesn't exist"
            }), 404
        tag = ChallengeTags.query.filter(func.lower(ChallengeTags.tag) == func.lower(tag_name),
                                         ChallengeTags.challenge_id == challenge_id).first()
        if tag:
            return jsonify({
                'status': "error",
                'message': "Tag already exists"
            }), 409

        checker = run_checks(is_authorized=challenge.submitter)
        if checker is not None:
            return jsonify(checker[0]), checker[1]

        new_tag = ChallengeTags.create(challenge_id, tag_name)
        return jsonify(new_tag), 201
    elif request.method == 'DELETE':
        challenge = Challenges.query.filter_by(id=challenge_id).first()
        if not challenge:
            return jsonify({
                'status': "error",
                'message': "Challenge doesn't exist"
            }), 404
        tag = ChallengeTags.query.filter(func.lower(ChallengeTags.tag) == func.lower(tag_name),
                                         ChallengeTags.challenge_id == challenge_id).first()
        if not tag:
            return jsonify({
                'status': "error",
                'message': "Tag doesn't exist"
            }), 409

        checker = run_checks(is_authorized=challenge.submitter)
        if checker is not None:
            return jsonify(checker[0]), checker[1]

        tag.delete()
        return '', 204

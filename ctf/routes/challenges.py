""" CTF - challenges.py

Contains the routes pertaining to the retrieval, creation, and removal of challenges
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import desc

from ctf import auth
from ctf.models import Challenge, Difficulty, Category
from ctf.utils import TSAPreCheck, delete_flags, delete_challenge_tags, get_all_challenge_data, \
    has_json_args
from ctf.constants import not_found

challenges_bp = Blueprint('challenges', __name__)


@challenges_bp.route('', methods=['GET'])
@auth.login_required
def all_challenges():
    """
    Get all challenges
    """
    # 'limit' and 'offset' URL parameters can be used to modify which challenges are returned
    limit = 10
    offset = 1
    if request.args.get('limit'):
        limit = int(request.args['limit'])
    if request.args.get('offset'):
        offset = int(request.args['offset'])

    precheck = TSAPreCheck()
    current_user = precheck.get_current_user()
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    return jsonify([
        get_all_challenge_data(challenge.id, current_user) for challenge in
        Challenge.query.order_by(desc(Challenge.id)).paginate(offset, limit).items
    ]), 200


@challenges_bp.route('', methods=['POST'])
@auth.login_required
@has_json_args("title", "description", "author", "difficulty", "category")
def create_challenge():
    """
    Creates a challenge given parameters in application/json body
    """
    data = request.get_json()
    category = Category.query.filter_by(name=data['category'].lower()).first()
    difficulty = Difficulty.query.filter_by(name=data['difficulty'].lower()).first()

    precheck = TSAPreCheck().ensure_existence((category, Category), (difficulty, Difficulty))
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    submitter = precheck.get_current_user()
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    new_challenge = Challenge.create(data['title'], data['description'], data['author'],
                                     submitter, difficulty, category)
    return jsonify(new_challenge), 201


@challenges_bp.route('/<int:challenge_id>', methods=['GET'])
@auth.login_required
def single_challenge(challenge_id: int):
    """
    Operations pertaining to a single challenge

    :GET: Get the challenge identified by 'challenge_id'
    :DELETE: Delete the challenge identified by 'challenge_id'
    """
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    precheck = TSAPreCheck().ensure_existence((challenge, Challenge))
    current_user = precheck.get_current_user()
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code
    return jsonify(get_all_challenge_data(challenge.id, current_user)), 200


@challenges_bp.route('/<int:challenge_id>', methods=['DELETE'])
@auth.login_required(role=['rtp', 'ctf'])
def delete_challenge(challenge_id: int):
    """
    Deletes the specified challenge
    """
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        return not_found()

    precheck = TSAPreCheck().is_authorized(challenge.submitter if challenge is not None else None)
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    delete_challenge_tags(challenge.id)
    delete_flags(challenge.id)
    challenge.delete()
    return '', 204

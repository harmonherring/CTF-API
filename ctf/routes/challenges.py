""" CTF - challenges.py

Contains the routes pertaining to the retrieval, creation, and removal of challenges
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import desc

from ctf import auth, db
from ctf.models import Challenge, Difficulty, Category, ChallengeTag
from ctf.utils import delete_flags, delete_challenge_tags, get_all_challenge_data, has_json_args, \
    expose_userinfo, is_ctf_admin
from ctf.constants import not_found, no_username, not_authorized

challenges_bp = Blueprint('challenges', __name__)


@challenges_bp.route('', methods=['GET'])
@auth.login_required
@expose_userinfo
def all_challenges(**kwargs):
    """
    Get all challenges
    """
    # 'limit' and 'offset' URL parameters can be used to modify which challenges are returned
    limit = 10
    offset = 1
    if limit_val := request.args.get('limit'):
        limit = int(limit_val)
    if offset_val := request.args.get('offset'):
        offset = int(offset_val)

    # Category and Difficulty parameters are a comma-separated list of categories/difficulties
    categories = []
    difficulties = []
    if category_names := request.args.get('categories'):
        categories = category_names.split(',')
    if difficulty_names := request.args.get('difficulties'):
        difficulties = difficulty_names.split(',')

    current_user = kwargs['userinfo'].get('preferred_username')
    if not current_user:
        return no_username()

    challenges = Challenge.query
    if categories:
        challenges = challenges.filter(Challenge.category_name.in_(categories))
    if difficulties:
        challenges = challenges.filter(Challenge.difficulty_name.in_(difficulties))
    challenges = challenges.order_by(desc(Challenge.id)).paginate(offset, limit).items

    return jsonify([
        get_all_challenge_data(challenge.id, current_user) for challenge in challenges
    ]), 200


@challenges_bp.route('', methods=['POST'])
@auth.login_required
@has_json_args("title", "description", "author", "difficulty", "category")
@expose_userinfo
def create_challenge(**kwargs):
    """
    Creates a challenge given parameters in application/json body
    """
    data = request.get_json()
    category = Category.query.filter_by(name=data['category'].lower()).first()
    difficulty = Difficulty.query.filter_by(name=data['difficulty'].lower()).first()

    if not (category and difficulty):
        return jsonify({
            'status': "error",
            'message': "The category or difficulty doesn't exist"
        }), 422

    submitter = kwargs['userinfo'].get('preferred_username')
    if not submitter:
        return no_username()

    new_challenge = Challenge.create(data['title'], data['description'], data['author'],
                                     submitter, difficulty, category)

    tags = []
    if tag_names := data.get('tags'):
        tags = list(dict.fromkeys(tag_names))
    for tag in tags:
        new_tag = ChallengeTag(new_challenge['id'], tag)
        db.session.add(new_tag)
    db.session.commit()

    return jsonify(new_challenge), 201


@challenges_bp.route('/<int:challenge_id>', methods=['GET'])
@auth.login_required
@expose_userinfo
def single_challenge(challenge_id: int, **kwargs):
    """
    Operations pertaining to a single challenge

    :GET: Get the challenge identified by 'challenge_id'
    :DELETE: Delete the challenge identified by 'challenge_id'
    """
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        return not_found()

    current_user = kwargs['userinfo'].get("preferred_username")
    if not current_user:
        return no_username()

    return jsonify(get_all_challenge_data(challenge.id, current_user)), 200


@challenges_bp.route('/<int:challenge_id>', methods=['DELETE'])
@auth.login_required
@expose_userinfo
def delete_challenge(challenge_id: int, **kwargs):
    """
    Deletes the specified challenge
    """
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        return not_found()

    current_username = kwargs['userinfo'].get('preferred_username')
    if not current_username:
        return no_username()
    groups = kwargs['userinfo'].get('groups')
    if (current_username != challenge.submitter) and (not is_ctf_admin(groups)):
        return not_authorized()

    delete_challenge_tags(challenge.id)
    delete_flags(challenge.id)
    challenge.delete()
    return jsonify({
        'status': "success"
    }), 200

""" CTF - challenges.py

Contains the routes pertaining to the retrieval, creation, and removal of challenges
"""

from flask import Blueprint, request, jsonify, session

from ctf import auth
from ctf.models import Challenge, Difficulty, Category
from ctf.utils import run_checks

challenges_bp = Blueprint('challenges', __name__)


@challenges_bp.route('/', methods=['GET', 'POST'])
@auth.oidc_auth
def all_challenges():
    """
    Operations involving challenges

    :GET: Get some challenges. Can be paginated with 'limit' and 'offset' URL parameters
    :POST: Create a challenge using the 'difficulty', 'category', 'title', 'description',
        'author', and 'submitter values passed in the application/json body
    """
    if request.method == 'GET':
        # 'limit' and 'offset' URL parameters can be used to modify which challenges are returned
        limit = 10
        offset = 1
        if request.args.get('limit'):
            limit = int(request.args['limit'])
        if request.args.get('offset'):
            offset = int(request.args['offset'])
        return jsonify([
            challenge.to_dict() for challenge in Challenge.query.paginate(offset, limit).items
        ]), 200
    elif request.method == 'POST':
        checker = run_checks(has_json_args=["title", "description", "author", "difficulty",
                                            "category"])
        if checker is not None:
            return jsonify(checker[0]), checker[1]

        data = request.get_json()
        category = Category.query.filter_by(name=data['category'].lower()).first()
        difficulty = Difficulty.query.filter_by(name=data['difficulty'].lower()).first()
        if not (category and difficulty):
            return jsonify({
                'status': "error",
                'message': "Nonexistent category or difficulty"
            }), 422
        submitter = session['userinfo'].get('preferred_username')
        new_challenge = Challenge.create(data['title'], data['description'], data['author'],
                                         submitter, difficulty, category)
        return jsonify(new_challenge), 201


@challenges_bp.route('/<int:challenge_id>', methods=['GET', 'DELETE'])
@auth.oidc_auth
def single_challenge(challenge_id: int):
    """
    Operations pertaining to a single challenge

    :GET: Get the challenge identified by 'challenge_id'
    :DELETE: Delete the challenge identified by 'challenge_id'
    """
    if request.method == 'GET':
        challenge = Challenge.query.filter_by(id=challenge_id).first()
        if challenge:
            return jsonify(challenge.to_dict()), 200
        else:
            return jsonify({
                'status': "error",
                'message': "Challenge doesn't exist"
            }), 404
    elif request.method == 'DELETE':
        challenge = Challenge.query.filter_by(id=challenge_id).first()
        if not challenge:
            return jsonify({
                'status': "error",
                'message': "Challenge doesn't exist"
            }), 404
        checker = run_checks(is_authorized=challenge.submitter)
        if checker is not None:
            return jsonify(checker[0]), checker[1]
        challenge.delete()
        return '', 204

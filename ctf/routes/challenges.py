""" CTF - challenges.py

Contains the routes pertaining to the retrieval, creation, and removal of challenges
"""

from flask import Blueprint, request, jsonify, session

from ctf import auth
from ctf.models import Challenges, Difficulties, Categories
from ctf.ldap import is_ctf_admin

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
            challenge.to_dict() for challenge in Challenges.query.paginate(offset, limit).items
        ]), 200
    elif request.method == 'POST':
        if not request.is_json:
            return jsonify({
                'status': "error",
                'message': "Content-Type must be application/json"
            }), 415
        data = request.get_json()
        if not (data.get('title') and data.get('description') and data.get('author') and
                data.get('difficulty') and data.get('category')):
            return jsonify({
                'status': "error",
                'message': "'title', 'description', 'author', 'difficulty', and 'category' "
                           "fields are required"
            }), 422
        category = Categories.query.filter_by(name=data['category'].lower()).first()
        difficulty = Difficulties.query.filter_by(name=data['difficulty'].lower()).first()
        if not (category and difficulty):
            return jsonify({
                'status': "error",
                'message': "Nonexistent category or difficulty"
            }), 422
        submitter = session['userinfo'].get('preferred_username')
        if not submitter:
            return jsonify({
                'status': "error",
                'message': "Your session doesn't include the 'preferred_username' value"
            }), 400
        new_challenge = Challenges.create(data['title'], data['description'], data['author'],
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
        challenge = Challenges.query.filter_by(id=challenge_id).first()
        if challenge:
            return jsonify(challenge.to_dict()), 200
        else:
            return jsonify({
                'status': "error",
                'message': "Challenge doesn't exist"
            }), 404
    elif request.method == 'DELETE':
        # Check to ensure that the deleter is an admin or the person who created the challenge
        current_username = session['userinfo'].get('preferred_username')
        challenge = Challenges.query.filter_by(id=challenge_id).first()
        if not challenge:
            return jsonify({
                'status': "error",
                'message': "Challenge doesn't exist"
            }), 404
        if not (is_ctf_admin(current_username) or (challenge.submitter == current_username)):
            return jsonify({
                'status': "error",
                'message': "You aren't authorized to delete this challenge"
            }), 403
        challenge.delete()
        return '', 204

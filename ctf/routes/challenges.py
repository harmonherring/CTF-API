""" CTF - challenges.py

Contains the routes pertaining to the retrieval, creation, and removal of challenges
"""
import os.path
import uuid
import threading

from flask import Blueprint, request, jsonify
from sqlalchemy import desc, asc
import magic
from werkzeug.utils import secure_filename

from ctf import auth, app
from ctf.models import Challenge, Difficulty, Category
from ctf.utils import delete_flags, delete_challenge_tags, get_all_challenge_data, expose_userinfo,\
    is_ctf_admin, has_formdata_args, s3_upload_and_create_challenge, delete_s3_object
from ctf.constants import not_found, no_username, not_authorized, invalid_mime_type, \
    missing_body_parts

challenges_bp = Blueprint('challenges', __name__)


@challenges_bp.route('', methods=['GET'])
@auth.login_required
@expose_userinfo
def all_challenges(**kwargs):
    """
    Get all challenges
    """
    # 'limit' and 'offset' URL parameters can be used to modify which challenges are returned
    try:
        limit = int(request.args.get('limit', default=10))
    except ValueError:
        limit = 10
    try:
        offset = int(request.args.get('offset', default=1))
    except ValueError:
        offset = 1
    search_query = request.args.get('search')
    sort_by = request.args.get('sort_by')
    order_by = request.args.get('order_by')

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
    if search_query:
        challenges = challenges.filter(
            getattr(Challenge, 'description').ilike(f'%{search_query}%') |
            getattr(Challenge, 'title').ilike(f'%{search_query}%') |
            getattr(Challenge, 'submitter').ilike(f'%{search_query}%')
        )
    order_op = asc if order_by == "asc" else desc
    if sort_by in ('date', 'ts'):
        sort_query = order_op(Challenge.ts)
    else:
        sort_query = order_op(Challenge.ts)
    challenges = challenges.order_by(sort_query).paginate(offset, limit, error_out=False).items

    return jsonify([
        get_all_challenge_data(challenge.id, current_user) for challenge in challenges
    ]), 200


@challenges_bp.route('', methods=['POST'])
@auth.login_required
@has_formdata_args("title", "description", "author", "difficulty", "category")
@expose_userinfo
def create_challenge(**kwargs):
    """
    Creates a challenge given parameters in application/json body
    """
    data = request.form.to_dict()
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

    file = request.files.get('file')
    if category.upload_required and not file:
        return missing_body_parts("multipart/form-data", "file")
    else:
        split = os.path.splitext(secure_filename(file.filename))
        filename = str(uuid.uuid4()) + str(split[len(split)-1])
        filepath = os.path.join(app.config['UPLOAD_PATH'], filename)
        file.save(filepath)

    mime = magic.Magic(mime=True)
    if not mime.from_file(filepath) in app.config['ALLOWED_MIME_TYPES']:
        return invalid_mime_type(mime.from_file(filepath))

    tags = []
    if tag_names := data.get('tags'):
        tags = list(dict.fromkeys(tag_names.split(",")))

    threading.Thread(
        target=s3_upload_and_create_challenge,
        args=(data['title'], data['description'], data['author'], submitter, difficulty, category,
              filename, tags)).start()

    return jsonify({
        'status': "success",
        'message': "Your submission has been added to the queue and will become visible when "
                   "processing is complete"
    }), 202


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

    if challenge.filename:
        threading.Thread(
            target=delete_s3_object,
            args=(challenge.filename,)
        ).start()

    delete_challenge_tags(challenge.id)
    delete_flags(challenge.id)
    challenge.delete()
    return jsonify({
        'status': "success"
    }), 200

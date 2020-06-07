""" CTF - utils.py

Contains useful functions used across many parts of the API
"""
import os
from functools import wraps

import requests
from flask import request, jsonify
import jwt
from werkzeug.utils import secure_filename

from ctf import db, auth, app, s3
from ctf.models import UsedHint, Hint, Solved, Flag, ChallengeTag, Challenge
from ctf.constants import CTF_ADMINS, missing_body_parts


@auth.verify_token
def verify_token(token):
    """
    Verifies that the given token came from a configured OIDC provider

    :param token: Token passed in the authorization header
    :return: The decoded payload
    """
    try:
        if jwt.decode(token, app.config['OIDC_PUBLIC_KEY'], algorithms='RS256'):
            return token
    except Exception as jwt_error:
        print(jwt_error)
        return None


@auth.get_user_roles
def get_user_roles(user: str):
    """
    Returns the roles that this user has.

    :param user: The access token handed by the client in the Authorization header
    :return: The roles that this user has
    :TODO: Scope access to certain endpoints
    """
    return get_userinfo(user).get('groups')


def get_userinfo(token: str) -> dict:
    """
    Calls the configured SSO userinfo endpoint and returns the data from there

    :param token: The authorization header to be sent
    :return: The information describing the current user
    """
    headers = {
        "Authorization": "Bearer " + token
    }
    userinfo = requests.get(app.config['OIDC_USERINFO_ENDPOINT'], headers=headers).json()
    current_username = userinfo.get('preferred_username')

    # Just in case an actual role called "ctf" exists...
    # TODO: Get an actual role created for this
    userinfo['groups'] = [group for group in userinfo['groups'] if group != 'ctf']

    if current_username in CTF_ADMINS:
        userinfo['groups'].append('ctf')
    return userinfo


@auth.error_handler
def auth_error(status):
    """
    Handles the authentication error return done by flask-httpauth

    :param status: status code of the auth error
    :return: JSON describing the error and the error code
    """
    if status == 401:
        return jsonify(
            {
                'status': "error",
                'message': "You aren't logged in"
            }
        ), status
    elif status == 403:
        return jsonify(
            {
                'status': "error",
                'message': "You aren't authorized to do that"
            }
        ), status
    else:
        return jsonify(
            {
                'status': "error",
                'message': "Access denied"
            }
        ), status


def has_json_args(*json_args):
    """
    Checks if the request has Content-Type set to application/json and specified arguments
    exist. Should only wrap a Flask route
    :param json_args: The arguments to check for
    :return: The Flask route if success, or jsonified error otherwise
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'status': "error",
                    'message': "Your Content-Type must be application/json"
                }), 415
            data: dict = request.get_json()
            missing = []
            for arg in json_args:
                if arg not in data.keys():
                    missing.append(arg)
            if missing:
                return missing_body_parts("application/json", *missing)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def has_formdata_args(*formdata_args, required_files: list = None):
    """
    Checks if the request has Content-Type set to multipart/form-data and specified arguments
    exist. Should only wrap a Flask route
    :param required_files: The files that should exist in the request
    :param formdata_args: The arguments to check for
    :return: The Flask route if success, or jsonified error otherwise
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not request.content_type.startswith('multipart/form-data'):
                return jsonify({
                    'status': "error",
                    'message': "Your Content-Type must be multipart/form-data"
                }), 415
            data: dict = request.form.to_dict()
            missing = []
            for arg in formdata_args:
                if not data.get(arg):
                    missing.append(arg)
            missing_files = []
            if required_files:
                files = request.files
                for file in required_files:
                    if not files.get(file):
                        missing_files.append(file)
            if missing:
                return missing_body_parts("multipart/form-data", *missing)
            if missing_files:
                return missing_body_parts("multipart/form-data", *missing_files)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def expose_userinfo(func):
    """
    Exposes the current user's username in the current_username kwarg of the wrapped function
    Must be called in conjunction with auth.login_required
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_token = auth.current_user()
        if not current_token:
            return jsonify({
                'status': "error",
                'message': "Not authenticated"
            }), 401
        userinfo = get_userinfo(current_token)
        return func(*args, **kwargs, userinfo=userinfo)
    return wrapper


def delete_used_hints(hint_id: int):
    """
    Deletes the used hints identified by 'hint_id'

    :param hint_id: The matching used hints should be deleted
    """
    for used_hint in UsedHint.query.filter_by(hint_id=hint_id).all():
        db.session.delete(used_hint)
    db.session.commit()


def delete_hints(flag_id: int):
    """
    Deletes hints identified by 'flag_id'.

    :param flag_id: The matching hints should be deleted
    """
    for hint in Hint.query.filter_by(flag_id=flag_id).all():
        delete_used_hints(hint.id)
        hint.delete()


def delete_hint(hint_id: int):
    """
    Deletes a single hint and its used hints

    :param hint_id: The id of the hint
    """
    delete_used_hints(hint_id)
    hint = Hint.query.filter_by(id=hint_id).first()
    if hint:
        hint.delete()


def delete_solved(flag_id: int):
    """
    Deletes solved relations identified by 'flag_id'

    :param flag_id: The matching solved relations should be deleted
    """
    for solved in Solved.query.filter_by(flag_id=flag_id).all():
        db.session.delete(solved)
    db.session.commit()


def delete_flags(challenge_id):
    """
    Removes the flags with matching 'challenge_id'

    :param challenge_id: The matching flags should be deleted
    """
    for flag in Flag.query.filter_by(challenge_id=challenge_id).all():
        delete_solved(flag.id)
        delete_hints(flag.id)
        flag.delete()


def delete_flag(flag_id: int):
    """
    Deletes a single flag identified by flag_id

    :param flag_id: Identifier of the flag to be deleted
    """
    flag = Flag.query.filter_by(id=flag_id).first()
    if flag:
        delete_solved(flag.id)
        delete_hints(flag.id)
        flag.delete()


def delete_challenge_tags(challenge_id: int):
    """
    Deletes all challenge tags with 'challenge_id'

    :param challenge_id: Tags with this challenge_id will be deleted
    """
    for tag in ChallengeTag.query.filter_by(challenge_id=challenge_id).all():
        db.session.delete(tag)
    db.session.commit()


def get_all_challenge_data(challenge_id: int, current_user: str):
    """
    Gets Challenge data, associated flags, and the hints associated with those flags
    """
    # This is a yikes
    challenge = Challenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        return None
    returnval = challenge.to_dict()
    if object_name := returnval['filename']:
        returnval['download'] = create_presigned_url(object_name)
    solved = [solved.flag_id for solved in Solved.query.filter_by(username=current_user).all()]
    used = [
        used_hint.hint_id for used_hint in UsedHint.query.filter_by(username=current_user).all()
    ]
    flags = challenge.flags
    returnval['flags'] = {flag.id: flag.to_dict() for flag in flags}
    for flag in returnval['flags']:
        if returnval['flags'][flag]['id'] not in solved:
            del returnval['flags'][flag]['flag']
        hints = Hint.query.filter_by(flag_id=flag).all()
        returnval['flags'][flag]['hints'] = {hint.id: hint.to_dict() for hint in hints}
        for hint in returnval['flags'][flag]['hints']:
            if returnval['flags'][flag]['hints'][hint]['id'] not in used:
                del returnval['flags'][flag]['hints'][hint]['hint']

    return returnval


def calculate_score(username: str) -> int:
    """
    Calculates the score for a user. Adds up points from solved challenges, subtracts points from
    spent hints
    """
    solved = Solved.query.filter_by(username=username).all()
    used_hints = UsedHint.query.filter_by(username=username).all()
    total_score = 0
    for solution in solved:
        total_score += solution.flag.point_value
    for hint in used_hints:
        if hint.hint.flag.challenge.submitter != username:
            total_score -= hint.hint.cost
    return total_score


def is_ctf_admin(groups: list) -> bool:
    """
    Quick function to determine if a user is an rtp or ctf admin

    :param groups: List of the user's groups
    :return: Boolean describing whether or not this user can administrate
    """
    if "rtp" in groups or "ctf" in groups:
        return True
    return False


def s3_upload_and_create_challenge(title: str, description: str, author: str, submitter: str,
                                   difficulty: str, category: str, filename: str, tags=None):
    """
    Uploads the file with matching filename from local storage to S3, then deletes the local copy
    :param title: Title of the Challenge
    :param description: Description of the Challenge
    :param author: The person who created this challenge
    :param submitter: The account that submitted this challenge
    :param difficulty: Text description of the difficulty. Must exist in Difficulties table.
    :param category: Text description of the category. Must exist in Categories table.
    :param filename: Name of the file associated with this Challenge and to be uploaded to S3
    :param new_filename: New name of the file when it's uploaded to S3
    :param tags: Optional tags to be created after the challenge
    """
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_PATH'], filename)

    if os.path.exists(filepath):
        s3.upload_file(filepath, app.config['S3_BUCKET'], filename)
        os.remove(filepath)
        new_challenge = Challenge.create(title, description, author, submitter, difficulty,
                                         category, filename)
        for tag in tags:
            new_tag = ChallengeTag(new_challenge['id'], tag)
            db.session.add(new_tag)
        db.session.commit()


def delete_s3_object(object_name):
    """
    Sends request to delete S3 object
    :param object_name: Name of object to delete
    """
    s3.delete_object(Bucket=app.config['S3_BUCKET'], Key=object_name)


def create_presigned_url(object_name, expiration=10800):
    """
    Creates a presigned URL for an S3 object
    :param object_name: object name to generate url for
    :param expiration: How long the link should be valid for
    :return: Presigned URL
    """
    try:
        params = {
            'Bucket': app.config['S3_BUCKET'],
            'Key': object_name
        }
        response = s3.generate_presigned_url('get_object', Params=params, ExpiresIn=expiration)
    except:
        return None
    return response

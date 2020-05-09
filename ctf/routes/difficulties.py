""" CTF - difficulties.py

Contains the API routes pertaining to the available challenge difficulties
"""

from flask import Blueprint, request, jsonify, session

from ctf import auth
from ctf.models import Difficulties
from ctf.ldap import is_ctf_admin

difficulties_bp = Blueprint("difficulties", __name__)


@difficulties_bp.route('/', methods=['GET', 'POST'])
@auth.oidc_auth
def all_difficulties():
    """
    Operations involving Difficulties

    :GET: Get all available difficulties
    :POST: Takes 'name' value from application/json body and creates a Difficulty
    """
    if request.method == 'GET':
        return jsonify([difficulty.to_dict()['name'] for difficulty in Difficulties.query.all()]),\
               200
    if request.method == 'POST':
        if not is_ctf_admin(session['userinfo'].get('preferred_username')):
            return jsonify({
                'status': "error",
                'message': "You aren't authorized to create Difficulties"
            }), 403
        if not request.is_json:
            return jsonify({
                'status': "error",
                'message': "Content-Type must be application/json"
            }), 415
        data = request.get_json()
        if not data.get('name'):
            return jsonify({
                'status': "error",
                'message': "'name' field is required"
            }), 422
        if Difficulties.query.filter_by(name=data['name']).first():
            return jsonify({
                'status': "error",
                'message': "Difficulty already exists"
            }), 409
        new_difficulty = Difficulties.create(data['name'])
        return jsonify(new_difficulty), 201


@difficulties_bp.route('/<difficulty_name>', methods=['DELETE'])
@auth.oidc_auth
def single_difficulty(difficulty_name: str):
    """
    Operations involving a single difficulty

    :DELETE: Deletes the Difficulty identified by difficulty_name
    """
    if request.method == 'DELETE':
        if not is_ctf_admin(session['userinfo'].get('preferred_username')):
            return jsonify({
                'status': "error",
                'message': "You aren't authorized to delete Difficulties"
            }), 403
        difficulty = Difficulties.query.filter_by(name=difficulty_name).first()
        if not difficulty:
            return jsonify({
                'status': "error",
                'message': "Difficulty doesn't exist"
            }), 404
        difficulty.delete()
        return '', 204

""" CTF - difficulties.py

Contains the API routes pertaining to the available challenge difficulties
"""

from flask import Blueprint, request, jsonify

from ctf import auth
from ctf.models import Difficulty
from ctf.utils import run_checks

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
        return jsonify([difficulty.to_dict()['name'] for difficulty in Difficulty.query.all()]),\
               200
    elif request.method == 'POST':
        checker = run_checks(is_authorized=None, has_json_args=["name"])
        if checker is not None:
            return jsonify(checker[0]), checker[1]
        data = request.get_json()
        if Difficulty.query.filter_by(name=data['name']).first():
            return jsonify({
                'status': "error",
                'message': "Difficulty already exists"
            }), 409
        new_difficulty = Difficulty.create(data['name'])
        return jsonify(new_difficulty), 201


@difficulties_bp.route('/<difficulty_name>', methods=['DELETE'])
@auth.oidc_auth
def single_difficulty(difficulty_name: str):
    """
    Operations involving a single difficulty

    :DELETE: Deletes the Difficulty identified by difficulty_name
    """
    if request.method == 'DELETE':
        checker = run_checks(is_authorized=None)
        if checker is not None:
            return jsonify(checker[0]), checker[1]
        difficulty = Difficulty.query.filter_by(name=difficulty_name).first()
        if not difficulty:
            return jsonify({
                'status': "error",
                'message': "Difficulty doesn't exist"
            }), 404
        difficulty.delete()
        return '', 204

""" CTF - difficulties.py

Contains the API routes pertaining to the available challenge difficulties
"""

from flask import Blueprint, request, jsonify

from ctf import auth
from ctf.models import Difficulty
from ctf.utils import TSAPreCheck

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
        data = request.get_json()
        check_difficulty = Difficulty.query.filter_by(name=data.get('name') if data.get('name')
                                                      else None)
        precheck = TSAPreCheck().is_authorized(None).has_json_args("name").ensure_nonexistence((
            check_difficulty, Difficulty))
        if precheck.error_code:
            return jsonify(precheck.message), precheck.error_code

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
        difficulty = Difficulty.query.filter_by(name=difficulty_name).first()
        precheck = TSAPreCheck().is_authorized(None).ensure_existence((difficulty, Difficulty))
        if precheck.error_code:
            return jsonify(precheck.message), precheck.error_code
        difficulty.delete()
        return '', 204

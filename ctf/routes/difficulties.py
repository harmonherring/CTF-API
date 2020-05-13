""" CTF - difficulties.py

Contains the API routes pertaining to the available challenge difficulties
"""

from flask import Blueprint, request, jsonify

from ctf import auth
from ctf.models import Difficulty
from ctf.utils import TSAPreCheck

difficulties_bp = Blueprint("difficulties", __name__)


@difficulties_bp.route('', methods=['GET'])
@auth.login_required
def all_difficulties():
    """
    Get all difficulties

    :GET: Get all available difficulties
    """
    return jsonify([difficulty.to_dict()['name'] for difficulty in Difficulty.query.all()]), 200


@difficulties_bp.route('', methods=['POST'])
@auth.login_required(role=['rtp', 'ctf'])
def create_difficulty():
    """
    Creates a difficulty

    Takes 'name' value from application/json body and creates a Difficulty
    """
    data = request.get_json()
    check_difficulty = Difficulty.query.filter_by(name=data.get('name') if data.get('name')
                                                  else None).first()
    precheck = TSAPreCheck().is_authorized(None).has_json_args("name").ensure_nonexistence((
        check_difficulty, Difficulty))
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    new_difficulty = Difficulty.create(data['name'])
    return jsonify(new_difficulty), 201


@difficulties_bp.route('/<difficulty_name>', methods=['DELETE'])
@auth.login_required(role=['rtp', 'ctf'])
def single_difficulty(difficulty_name: str):
    """
    Deletes a difficulty
    """
    difficulty = Difficulty.query.filter_by(name=difficulty_name).first()
    precheck = TSAPreCheck().ensure_existence((difficulty, Difficulty))
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code
    difficulty.delete()
    return '', 204

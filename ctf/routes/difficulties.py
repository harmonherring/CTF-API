""" CTF - difficulties.py

Contains the API routes pertaining to the available challenge difficulties
"""

from flask import Blueprint, request, jsonify

from ctf import auth
from ctf.models import Difficulty
from ctf.utils import has_json_args
from ctf.constants import collision, not_found

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
@has_json_args("name")
def create_difficulty():
    """
    Creates a difficulty

    Takes 'name' value from application/json body and creates a Difficulty
    """
    data = request.get_json()

    check_difficulty = Difficulty.query.filter_by(name=data['name'].lower()).first()
    if check_difficulty:
        return collision()

    new_difficulty = Difficulty.create(data['name'].lower())
    return jsonify(new_difficulty), 201


@difficulties_bp.route('/<difficulty_name>', methods=['DELETE'])
@auth.login_required(role=['rtp', 'ctf'])
def single_difficulty(difficulty_name: str):
    """
    Deletes a difficulty
    """
    difficulty = Difficulty.query.filter_by(name=difficulty_name).first()

    if not difficulty:
        return not_found()

    difficulty.delete()
    return '', 204

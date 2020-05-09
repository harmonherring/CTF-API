""" CTF - solved.py

These API routes are poorly named. They keep a record of who has solved which flags.
"""

from flask import Blueprint, jsonify, request

from ctf import auth
from ctf.models import Solved, Flags

solved_bp = Blueprint('solved', __name__)


@solved_bp.route('/<int:flag_id>', methods=['GET'])
@auth.oidc_auth
def solved_flags(flag_id: int):
    """
    Operations pertaining to the solution of flags

    :GET: Get a list of the users who have solved this flag
    """
    if not Flags.query.filter_by(id=flag_id).first():
        return jsonify({
            'status': "error",
            'message': "Flag doesn't exist"
        }), 404
    if request.method == 'GET':
        return jsonify([solved.to_dict()['username'] for solved in Solved.query.filter_by(
            flag_id=flag_id).all()]), 200

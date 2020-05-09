"""CTF - categories.py

Contains the routes pertaining to the categories a challenge can fit in to
"""
from flask import Blueprint, jsonify, request

from ctf import auth
from ctf.models import Categories
from ctf.utils import run_checks

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/', methods=['GET', 'POST'])
@auth.oidc_auth
def all_categories():
    """
    Operations relating categories

    :GET: Returns all categories
    :POST: Takes 'name' and 'description' values from application/json body and creates a new
        category
    """
    if request.method == 'GET':
        return jsonify([category.to_dict() for category in Categories.query.all()]), 200
    elif request.method == 'POST':
        checker = run_checks(is_authorized=None, has_json_args=["name", "description"])
        if checker is not None:
            return jsonify(checker[0]), checker[1]
        data = request.get_json()
        if Categories.query.filter_by(name=data['name']).first():
            return jsonify({
                'status': "error",
                'message': "Category already exists"
            }), 409
        new_category = Categories.create(data['name'].lower(), data['description'])
        return jsonify(new_category), 201


@categories_bp.route('/<category_name>', methods=['GET', 'DELETE'])
@auth.oidc_auth
def single_category(category_name: str):
    """
    Operations relating to a single category

    :param category_name: Name of the category requested

    :GET: Returns the category's values
    :DELETE: Deletes the category
    """
    category = Categories.query.filter_by(name=category_name).first()
    if not category:
        return jsonify({
            'status': "error",
            'message': "Category doesn't exist"
        }), 404
    if request.method == 'GET':
        return jsonify(category.to_dict()), 200
    elif request.method == 'DELETE':
        checker = run_checks(is_authorized=None)
        if checker is not None:
            return jsonify(checker[0]), checker[1]
        category.delete()
        return '', 204

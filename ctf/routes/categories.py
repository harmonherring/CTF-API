"""CTF - categories.py

Contains the routes pertaining to the categories a challenge can fit in to
"""
from flask import Blueprint, jsonify, request, session

from ctf import auth
from ctf.models import Categories
from ctf.ldap import is_ctf_admin

categories_bp = Blueprint('categories_bp', __name__)


@categories_bp.route('/', methods=['GET', 'POST'])
@auth.oidc_auth
def all_categories():
    """
    Operations relating categories

    :GET: Returns all categories
    :POST: Takes 'name' and 'description' values from application/json body and creates a new
        category
    """
    print(session['userinfo'].get('preferred_username'))
    if request.method == 'GET':
        return jsonify([category.to_dict() for category in Categories.query.all()]), 200
    elif request.method == 'POST':
        if not is_ctf_admin(session['userinfo'].get('preferred_username')):
            return jsonify({
                'status': "error",
                'message': "You aren't authorized to create categories"
            }), 403
        if not request.is_json:
            return jsonify({
                'status': "error",
                'message': "Content-Type must be application/json"
            }), 415
        data = request.get_json()
        if not data['name'] and data['description']:
            return jsonify({
                'status': "error",
                'message': "'name' and 'description' fields are required"
            }), 422
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
        if not is_ctf_admin(session['userinfo'].get('preferred_username')):
            return jsonify({
                'status': "error",
                'message': "You aren't authorized to create categories"
            }), 403
        category.delete()
        return '', 204

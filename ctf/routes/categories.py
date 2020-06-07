"""CTF - categories.py

Contains the routes pertaining to the categories a challenge can fit in to.
"""
from flask import Blueprint, jsonify, request

from ctf import auth
from ctf.models import Category, Challenge
from ctf.utils import has_json_args
from ctf.constants import not_found, collision

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('', methods=['GET'])
@auth.login_required
def get_all_categories():
    """
    Get all categories

    TODO: Might be a good idea to give each category an id and have Challenges hold that id instead
        of name
    """
    categories = [category.to_dict() for category in Category.query.all()]
    for category in categories:
        category['count'] = Challenge.query.filter_by(category_name=category['name']).count()
    return jsonify(categories), 200


@categories_bp.route('', methods=['POST'])
@auth.login_required(role=['rtp', 'ctf'])
@has_json_args("name", "description")
def create_new_category():
    """
    Create a new category given parameters in application/json body
    """
    data = request.get_json()

    check_existing_category = Category.query.filter_by(name=data['name'].lower()).first()
    if check_existing_category:
        return collision()

    upload_required = bool(data.get("upload_required"))

    new_category = Category.create(data['name'].lower(), data['description'], upload_required)
    return jsonify(new_category), 201


@categories_bp.route('/<category_name>', methods=['GET'])
@auth.login_required
def get_category(category_name: str):
    """
    Operations relating to a single category

    :param category_name: Name of the category requested

    :GET: Returns the category's values
    :DELETE: Deletes the category
    """
    category = Category.query.filter_by(name=category_name.lower()).first()
    if not category:
        return not_found()
    return jsonify(category.to_dict()), 200


@categories_bp.route('/<category_name>', methods=['DELETE'])
@auth.login_required(role=['rtp', 'ctf'])
def delete_category(category_name: str):
    """
    Delete the specified category
    """
    category = Category.query.filter_by(name=category_name.lower()).first()
    if not category:
        return not_found()

    if Challenge.query.filter_by(category_name=category_name.lower()).first():
        return jsonify({
            'status': "error",
            'message': "You can't delete a category unless no challenges exist in that category"
        }), 409

    category.delete()
    return jsonify({
        'status': "success"
    }), 200

"""CTF - categories.py

Contains the routes pertaining to the categories a challenge can fit in to.
"""
from flask import Blueprint, jsonify, request

from ctf import auth
from ctf.models import Category
from ctf.utils import has_json_args
from ctf.constants import not_found, collision

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('', methods=['GET'])
@auth.login_required
def get_all_categories():
    """
    Get all categories
    """
    return jsonify([category.to_dict() for category in Category.query.all()]), 200


@categories_bp.route('', methods=['POST'])
@auth.login_required(role=['rtp', 'ctf'])
@has_json_args("name", "description")
def create_new_category():
    """
    Create a new category given parameters in application/json body
    """
    data = request.get_json()

    check_existing_category = Category.query.filter_by(name=data['name']).first()
    if check_existing_category:
        return collision()

    new_category = Category.create(data['name'].lower(), data['description'])
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
    category = Category.query.filter_by(name=category_name).first()
    if not category:
        return not_found()
    return jsonify(category.to_dict()), 200


@categories_bp.route('/<category_name>', methods=['DELETE'])
@auth.login_required(role=['rtp', 'ctf'])
def delete_category(category_name: str):
    """
    Delete the specified category
    """
    category = Category.query.filter_by(name=category_name).first()
    if not category:
        return not_found()
    category.delete()
    return '', 204

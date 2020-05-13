"""CTF - categories.py

Contains the routes pertaining to the categories a challenge can fit in to.
"""
from flask import Blueprint, jsonify, request

from ctf import auth
from ctf.models import Category
from ctf.utils import TSAPreCheck

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('', methods=['GET', 'OPTIONS'])
@auth.login_required
def get_all_categories():
    """
    Get all categories
    """
    return jsonify([category.to_dict() for category in Category.query.all()]), 200


@categories_bp.route('', methods=['POST'])
@auth.login_required
def create_new_category():
    """
    Create a new category given parameters in application/json body
    """
    precheck = TSAPreCheck().is_authorized(None).has_json_args("name", "description")
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

    data = request.get_json()
    check_existing_category = Category.query.filter_by(name=data['name']).first()
    precheck.ensure_nonexistence((check_existing_category, Category))
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code

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
        return jsonify({
            'status': "error",
            'message': "Category doesn't exist"
        }), 404
    return jsonify(category.to_dict()), 200


@categories_bp.route('/<category_name>', methods=['DELETE'])
@auth.login_required(role=['rtp', 'ctf'])
def delete_category(category_name: str):
    """
    Delete the specified category
    """
    category = Category.query.filter_by(name=category_name).first()
    if not category:
        return jsonify({
            'status': "error",
            'message': "Category doesn't exist"
        }), 404
    category.delete()
    return '', 204

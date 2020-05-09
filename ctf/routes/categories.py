"""CTF - categories.py

Contains the routes pertaining to the categories a challenge can fit in to
"""
from flask import Blueprint, jsonify, request

from ctf import auth
from ctf.models import Category
from ctf.utils import TSAPreCheck

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
        return jsonify([category.to_dict() for category in Category.query.all()]), 200
    elif request.method == 'POST':
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


@categories_bp.route('/<category_name>', methods=['GET', 'DELETE'])
@auth.oidc_auth
def single_category(category_name: str):
    """
    Operations relating to a single category

    :param category_name: Name of the category requested

    :GET: Returns the category's values
    :DELETE: Deletes the category
    """
    category = Category.query.filter_by(name=category_name).first()
    precheck = TSAPreCheck().ensure_existence((category, Category))
    if precheck.error_code:
        return jsonify(precheck.message), precheck.error_code
    if request.method == 'GET':
        return jsonify(category.to_dict()), 200
    elif request.method == 'DELETE':
        precheck.is_authorized(None)
        if precheck.error_code:
            return jsonify(precheck.message), precheck.error_code
        category.delete()
        return '', 204

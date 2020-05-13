""" CTF - constants.py

Contains constant values
"""
from flask import jsonify


def collision():
    """
    Return data for a collision
    """
    return jsonify({
        'status': "error",
        'message': "The requested resource already exists"
    }), 409


def not_found():
    """
    Return data when resource isn't found
    """
    return jsonify({
        'status': "error",
        'message': "The requested resource doesn't exist"
    }), 404

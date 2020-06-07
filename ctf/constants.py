""" CTF - constants.py

Contains constant values
"""
from flask import jsonify

CTF_ADMINS = ["harmon"]


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


def not_authorized():
    """
    Return data for when a user isn't authorized to do something
    """
    return jsonify({
        'status': "error",
        'message': "You aren't authorized to perform that action"
    }), 403


def no_username():
    """
    Return data for when someone doesn't have the preferred_username value in their userinfo
    """
    return jsonify({
        'status': "error",
        'message': "I can't figure out what your username is"
    }), 401


def invalid_mime_type():
    """
    Return data when the user uploads a disallowed file type
    """
    return jsonify({
        'status': "error",
        'message': "Invalid file type"
    }), 422


def missing_body_parts(body_type: str, *args):
    """
    Return data when user is missing required parts of the request body
    :param body_type: Required request body type
    :param args: Missing arguments
    """
    return jsonify({
        'status': "error",
        'message': "Missing the following arguments in your " + body_type + " body: " +
                   ', '.join([str(arg) for arg in args])
    }), 422

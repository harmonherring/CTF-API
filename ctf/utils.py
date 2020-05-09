""" CTF - utils.py

Contains useful functions used across many parts of the API
"""
from flask import request, session

from ctf.ldap import is_ctf_admin


def run_checks(**kwargs) -> (dict, int):
    """
    Runs the checks specified, return errors if needed, return None if all checks pass
    Most of these checks will fail if not run inside of a Flask route.
    """
    keys = kwargs.keys()
    if "is_authorized" in keys:
        # Check to see if current user is admin or is the user specified by associated kwarg
        if kwargs['is_authorized']:
            current_user = session['userinfo'].get('preferred_username')
            if not current_user:
                return {
                    'status': "error",
                    'message': "Your session doesn't have the 'preferred_username' value"
                }, 401
            if not (is_ctf_admin(current_user) or current_user == kwargs['is_authorized']):
                return {
                    'status': "error",
                    'message': "You aren't authorized for this action"
                }, 403
    if "has_json_args" in keys:
        if not request.is_json:
            return {
                'status': "error",
                'message':
                    kwargs['is_json'] if kwargs.get('is_json') else
                    "Content-Type must be application/json"
            }, 415
        if kwargs['has_json_args']:
            data = request.get_json()
            missing_args = []
            for json_arg in kwargs['has_json_args']:
                if not data.get(json_arg):
                    missing_args.append(json_arg)
            if len(missing_args) > 0:
                return {
                    'status': "error",
                    'message': "You're missing at least one of the required arguments in your "
                               "application/json body: " + ', '.join([str(missing_arg) for
                                                                      missing_arg in missing_args])
                }, 422

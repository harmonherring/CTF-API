""" CTF - utils.py

Contains useful functions used across many parts of the API
"""
from typing import Tuple, Any, Type

from flask import request, session
from flask_sqlalchemy import Model

from ctf.ldap import is_ctf_admin


def run_checks(**kwargs) -> (dict, int):
    """
    Runs the checks specified, return errors if needed, return None if all checks pass
    Most of these checks will fail if not run inside of a Flask route.
    """
    keys = kwargs.keys()
    print(keys)
    print("IS IT HERE: " + str("ensure_existence" in keys))
    if "is_authorized" in keys:
        # Check to see if current user is admin or is the user specified by associated kwarg
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
    if "ensure_existence" in keys:
        print("Ensuring existence")
        # This test ensures that the objects passed into the associated kwargs list exist.
        for argument in kwargs['ensure_existence']:
            print(argument)
            if not argument:
                return {
                    'status': "error",
                    'message': argument.__class__.__name__ + " does not exist"
                }, 404
    if "ensure_nonexistence" in keys:
        # This test ensures that the obejcts passed into the associated kwargs list don't exist
        for argument in kwargs['ensure_nonexistence']:
            if argument:
                return {
                    'status': "error",
                    'message': argument.__clas__.__name__ + " already exists"
                }, 409


class TSAPreCheck:
    """
    Contains the functions for performing various checks. Most of these checks require access to
    the session and request Flask objects. As such, this object should only ever exist inside of
    a Flask route
    """
    error_code = 0
    message = dict()

    def __init__(self):
        """
        Initializes a Precheck with no error code and an empty message
        """
        self.error_code = 0
        self.message = dict()

    def reset(self):
        """
        Resets this Precheck to its original state
        """
        self.error_code = 0
        self.message = dict()

    def is_authorized(self, user: str or None):
        """
        Uses the FLask session to determine if the current user is a CTF administrator, an RTP,
        or the person passed as the 'user' parameter
        :param user: The user who the current user should be
        """
        if self.error_code:
            return self
        current_user = session['userinfo'].get('preferred_username')
        if not current_user:
            self.error_code = 401
            self.message = {
                'status': "error",
                'message': "Your session doesn't have the 'preferred_username' value"
            }
        if not (is_ctf_admin(current_user) or current_user == user):
            self.error_code = 403
            self.message = {
                'status': "error",
                'message': "You aren't authorized for this action"
            }
        return self

    def has_json_args(self, *args):
        """
        Checks the request to ensure the Content-Type is application/json and then iterates over
        every value specified in *args and ensures it exists in the request body
        """
        if self.error_code:
            return self
        if not request.is_json:
            self.error_code = 415
            self.message = {
                'status': "error",
                'message': "Content-Type must be application/json"
            }
        data = request.get_json()
        missing_args = []
        for json_arg in args:
            if not data.get(json_arg):
                missing_args.append(json_arg)
        if len(missing_args) > 0:
            self.error_code = 422
            self.message = {
                'status': "error",
                'message': "You're missing at the following required arguments in your "
                           "application/json body: " + ', '.join([str(missing_arg) for
                                                                  missing_arg in missing_args])
                }
        return self

    def ensure_existence(self, *args: Tuple[Any, Type[Model]]):
        """
        Accepts tuples, where the first value is the arg to test the existence of, and the second
        value is the table model it belongs to (for error message purposes).
        This is primarily used for determining if anything was returned from a database query
        """
        if self.error_code:
            return self
        for query in args:
            if not query[0]:
                self.error_code = 404
                self.message = {
                    'status': "error",
                    'message': query[1].__name__ + " does not exist"
                }
        return self

    def ensure_nonexistence(self, *args: Tuple[Any, Type[Model]]):
        """
        Accepts tuples, where the first value is the arg to test the nonexistence of, and the second
        value is the table model it belongs to (for error message purposes).
        This is primarily used for ensuring nothing is returned from a database query
        """
        if self.error_code:
            return self
        for query in args:
            if query[0] is not None:
                self.error_code = 409
                self.message = {
                    'status': "error",
                    'message': query[1].__name__ + " already exists"
                }
        return self

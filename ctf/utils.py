""" CTF - utils.py

Contains useful functions used across many parts of the API
"""
from typing import Tuple, Any, Type, Union

from flask import request, session
from flask_sqlalchemy import Model

from ctf.ldap import is_ctf_admin


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

    def get_current_user(self) -> Union[str, None]:
        """
        Returns the current user. If unable to get the current username, returns an instance of
        self and sets 'error_code' and 'message' appropriately.
        """
        userinfo = session.get('userinfo')
        if userinfo:
            current_user = userinfo.get('preferred_username')
            if current_user:
                return current_user
        self.error_code = 401
        self.message = {
            'status': "error",
            'message': "Either the 'userinfo' or 'preferred_username' values don't exist in your "
                       "session"
        }
        return None

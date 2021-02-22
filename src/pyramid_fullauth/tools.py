# Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Additional tools used in pyramid_fullauth."""

import string
from random import choice

from pyramid_fullauth.exceptions import (
    EmptyError,
    ShortPasswordError,
    PasswordConfirmMismatchError,
)


def password_generator(length, chars=(string.ascii_letters + string.digits + string.punctuation)):
    """
    Generate random password.

    .. warning::

        TODO: tests!

    :param int length: length of a password to Generates
    :param list chars: list of characters from which to choose
    :returns: password
    :rtype: str
    """
    return "".join([choice(chars) for i in range(length)])


def validate_passsword(request, password, user=None):
    """
    Validate password properly.

    .. note::

        If no user provided, password is just validated

    :param pyramid.request.Request request: request object
    :param str password: password to be set
    :param pyramid_fullauth.models.User user: user object

    :raises: pyramid_fullauth.exceptions.ValidateError
    """
    password_config = request.registry["fullauth"]["register"]["password"]
    if not password:
        raise EmptyError(request._("Please enter your password", domain="pyramid_fullauth"))

    if password_config["length_min"] and len(password) < password_config["length_min"]:
        raise ShortPasswordError(request._("Password is too short", domain="pyramid_fullauth"))

    # here if password doesn't match
    if password_config["confirm"]:
        confirm_password = request.POST.get("confirm_password", "")
        if password != confirm_password:
            raise PasswordConfirmMismatchError(
                request._(
                    "password-mismatch",
                    default="Passwords don't match",
                    domain="pyramid_fullauth",
                )
            )

    if user:
        user.password = password

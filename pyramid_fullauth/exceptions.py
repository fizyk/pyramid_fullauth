# Copyright (c) 2013 - 2014 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Fullauth's exceptions definition."""


class DeleteException(Exception):

    """Exception risen when the user can't be deleted."""

    pass


class ValidateError(ValueError):

    """Base of every validate error in pyramid_fullauth."""

    pass


class EmptyError(ValidateError):

    """Thrown whenever user is trying to set empty value."""

    pass


class ShortPasswordError(ValidateError):

    """Thrown when password doesn't meet the length requirement."""

    pass


class PasswordConfirmMismatchError(ValidateError):

    """Thrown when there's a mismatch with cpassword_confirm."""

    pass


class EmailValidationError(ValidateError):

    """Exception thrown, when there's incorrect email provided."""

    pass

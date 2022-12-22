# Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Mixin's main module."""

from pyramid_fullauth.models.mixins.password import UserPasswordMixin
from pyramid_fullauth.models.mixins.email import UserEmailMixin

__all__ = ("UserPasswordMixin", "UserEmailMixin")

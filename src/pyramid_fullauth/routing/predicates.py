# Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Routing predicate definitions."""

from sqlalchemy.orm.exc import NoResultFound
from pyramid.predicates import CheckCSRFTokenPredicate
from pyramid.httpexceptions import HTTPUnauthorized
import pyramid_basemodel

from pyramid_fullauth.models import User


class UserPathHashRoutePredicate(object):
    """Check reset hash from url."""

    def __init__(self, val, _):
        self.val = val

    def text(self):
        """Predicate's representation."""
        return "user_path_hash = %s" % (self.val,)

    phash = text

    def __call__(self, context, _):
        """
        Check whether hash is correct and fits configured user attribute.

        :param dict context: pyramid info dict with path fragments and info
        :param pyramid.request.Request _: request object

        :returns: whether reset hash exists or not
        :rtype: bool

        """
        passed_hash = context["match"].get("hash", None)
        if passed_hash:
            try:
                context["match"]["user"] = (
                    pyramid_basemodel.Session.query(User)
                    .filter(getattr(User, self.val) == passed_hash)
                    .one()
                )
                return True
            except NoResultFound:
                pass
        return False


class CSRFCheckPredicate(CheckCSRFTokenPredicate):
    """
    Run csrf check dependant on configuration.

    .. note::

        Raises HTTPUnauthorized exception if check fails.

    :raises: pyramid.httpexceptions.HTTPUnauthorized

    :returns: True if check succeeds or turned off.
    :rtype: bool

    """

    def __call__(self, context, request):
        """
        Run predicate check.

        :param context:
        :param pyramid.request.Request request:

        """
        if request.registry["fullauth"]["check_csrf"]:
            result = CheckCSRFTokenPredicate.__call__(self, context, request)
            if not result:
                raise HTTPUnauthorized

        return True

# Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Auth related methods and classes."""

from pyramid.authorization import Allow, Everyone, ALL_PERMISSIONS


def groupfinder(userid, request):
    """
    Read all user's groups.

    .. note::

        Adds **s:inactive** group to users who has not activated their account, and **s:user** group to those, who did.
        If user has is_admin flag, he gets **s:superadmin** group set

        Might be useful, when you want restrict access to some parts of your application, but still allow log in, and
        access to some other parts.

    :param int userid: user identity
    :param pyramid.request.Request request: request object
    :returns: list of groups
    :rtype: list
    """
    user = request.user
    groups = []
    if user and user.id == userid:
        groups = [group.name for group in user.groups]

        # let's add inactive group for users that have not activated their account

        if user.is_admin:
            groups.append("s:superadmin")

        if user.is_active:
            groups.append("s:user")
        else:
            groups.append("s:inactive")

        return groups
    return None


class BaseACLRootFactoryMixin(object):
    """
    ACL list factory Mixin.

    __acl__ is the attribute which stores the list.

    :return: tuple (Allow|Deny, Group name, Permission)
    :rtype: list

    .. note::

        Can be converted later to database stored (sqlalchemy session is accessible through request.db)
    """

    __acl__ = [
        (Allow, Everyone, "view"),
        (Allow, "s:superadmin", ALL_PERMISSIONS),
        (Allow, "s:user", ("password_change", "email_change")),
    ]

    def __init__(self, request):
        """Assing request as instance attribute."""
        self.request = request

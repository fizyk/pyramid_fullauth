# Copyright (c) 2013 - 2014 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""These method gets added to each ``pyramid.request.Request`` object."""

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.security import remember, forget
from sqlalchemy.sql.expression import func
from sqlalchemy.orm.exc import NoResultFound
import pyramid_basemodel

from pyramid_fullauth.models import User


def login_perform(request, user, location=None, remember_me=False):
    """
    Perform login action.

    :param pyramid.request.Request request: a request object
    :param pyramid_fullauth.models.User user: a user object
    :param str location: where user should be redirected after login
    :param bool remember_me: if True set cookie max_age to one month (60 * 60 * 24 * 30 seconds)

    :returns: redirect exception
    :rtype: pyramid.httpexceptions.HTTPSeeOther
    """
    user.logged_at = func.now()
    if remember_me:  # if remember in POST set cookie timeout to one from configure
        headers = remember(request, user.id,
                           max_age=request.registry['config'].fullauth.login.cookie_max_age)
    else:
        headers = remember(request, user.id)
    if not location:
        location = '/'

    # this remembers user immediately, without the need to redirect (see below)
    request.response.headers.extend(headers)
    return HTTPSeeOther(location=location, headers=request.response.headers)


def user(request):
    """
    Return user object.

    When called for the first time, it queries for user, which is later available as a pure property
    overriding this method. See :meth:`pyramid_fullauth.includeme` for logic behind property.

    :returns: logged in user object, or None
    :rtype: pyramid_fullauth.models.User
    """
    if request.unauthenticated_userid:
        try:
            user = pyramid_basemodel.Session.query(User).filter(
                User.id == request.unauthenticated_userid
            ).one()
            return user
        except NoResultFound:  # pragma: no cover
            pass


def logout(request):
    """
    Log user out.

    :param pyramid.request.Request request: a request object
    """
    if request.user:
        request.response.headerlist.extend(forget(request))
        request.user = None

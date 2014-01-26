# -*- coding: utf-8 -*-

# Copyright (c) 2013 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT

'''
    These method gets added to each ``pyramid.request.Request`` object
'''

from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.security import authenticated_userid
from pyramid.security import unauthenticated_userid

from sqlalchemy.sql.expression import func

from sqlalchemy.orm.exc import NoResultFound

from pyramid_basemodel import Session
from pyramid_fullauth.models import User


def login_perform(request, user, location=None, remember_me=False):
    '''
        Performs login action

        :param pyramid.request.Request request: a request object
        :param pyramid_fullauth.models.User user: a user object
        :param str location: where user should be redirected after login
        :param bool remember_me: if True set cookie max_age to one month (60 * 60 * 24 * 30 seconds)

        :returns: redirect exception
        :rtype: pyramid.httpexceptions.HTTPFound
    '''
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
    return HTTPFound(location=location, headers=request.response.headers)


def user(request):
    '''
        When called for the first time, it queries for user, which is later available as a pure property
        overriding this method

        :returns: logged in user object, or None
        :rtype: pyramid_fullauth.models.User
    '''
    userid = unauthenticated_userid(request)
    if userid:
        try:
            user = Session.query(User).filter(User.id == userid).one()
            return user
        except NoResultFound:  # pragma: no cover
            pass

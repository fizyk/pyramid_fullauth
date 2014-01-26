# -*- coding: utf-8 -*-

# Copyright (c) 2013 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT


from sqlalchemy.orm.exc import NoResultFound
from pyramid_basemodel import Session
from pyramid_fullauth.models import User
from pyramid.config.predicates import CheckCSRFTokenPredicate
from pyramid.httpexceptions import HTTPUnauthorized


def reset_hash(info, request):
    '''
        Checks whether reset hash is correct

        :param dict info: pyramid info dict with path fragments and info
        :param pyramid.request.Request request: request object
    '''

    reset_hash = info['match'].get('hash', None)
    if reset_hash:
        try:
            info['match']['user'] = Session.query(User).filter(User.reset_key == reset_hash).one()
            return True
        except NoResultFound:
            pass
    return False


def change_email_hash(info, request):
    '''
        Checks whether change email hash is correct

        :param dict info: pyramid info dict with path fragments and info
        :param pyramid.request.Request request: request object
    '''

    change_email_hash = info['match'].get('hash', None)
    if change_email_hash:
        try:
            info['match']['user'] = Session.query(User).filter(User.email_change_key == change_email_hash).one()
            return True
        except NoResultFound:
            pass
    return False


class CSRFCheckPredicate(CheckCSRFTokenPredicate):

    '''
    Runs csrf check dependant on configuration.
    Raises HTTPUnauthorized exception if check fails.

    :raises: pyramid.httpexceptions.HTTPUnauthorized
    :returns: True if check succeeds or turned off.
    :rtype: bool
    '''

    def __call__(self, context, request):

        if request.registry['config'].fullauth.check_csrf:
            result = CheckCSRFTokenPredicate.__call__(self, context, request)
            if not result:
                raise HTTPUnauthorized

        return True

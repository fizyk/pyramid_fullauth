# -*- coding: utf-8 -*-

# Copyright (c) 2013 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT


from sqlalchemy.orm.exc import NoResultFound
from pyramid_basemodel import Session

from pyramid_fullauth.models import User


def activate_hash(info, request):
    '''
        Checks whether activate hash is correct

        :param dict info: pyramid info dict with path fragments and info
        :param pyramid.request.Request request: request object
    '''

    activate_hash = info['match'].get('hash', None)
    if activate_hash:
        try:
            info['match']['user'] = Session.query(User).filter(User.activate_key == activate_hash).one()
            return True
        except NoResultFound:
            pass
    return False


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

# -*- coding: utf-8 -*-

# Copyright (c) 2013 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT

import logging

from tzf.pyramid_yml import config_defaults
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig


from pyramid_fullauth.auth import groupfinder
from pyramid_fullauth.routing import predicates
from pyramid_fullauth.request import login_perform
from pyramid_fullauth.request import user

__version__ = '0.2.3'


logger = logging.getLogger(__name__)


def includeme(configurator):
    '''
    pyramid_fullauth includeme method

    :param pyramid.configurator.Configurator configurator: pyramid's configurator object
    '''

    config_defaults(configurator, 'pyramid_fullauth:config')
    configurator.include('pyramid_localize')
    configurator.include('pyramid_mako')
    fullauth_config = configurator.registry['config'].fullauth

    configurator.set_authorization_policy(ACLAuthorizationPolicy())
    configurator.set_authentication_policy(
        AuthTktAuthenticationPolicy(callback=groupfinder,
                                    **fullauth_config.AuthTkt))

    # loading and setting session factory
    # first, divide provided path for module, and factory name
    module, factory = fullauth_config.session.factory.rsplit('.', 1)
    # import session module first
    session_module = __import__(module, fromlist=[module])
    # get the  factory class
    session_factory = getattr(session_module, factory)

    # set the new session factory
    configurator.set_session_factory(
        session_factory(**fullauth_config.session.settings))

    configurator.add_view_predicate('check_csrf', predicates.CSRFCheckPredicate)

    # add routes
    configurator.add_route(name='login', pattern='/login')
    configurator.add_route(name='logout', pattern='/logout')
    configurator.add_route(name='register', pattern='/register')
    configurator.add_route(name='register:activate', pattern='/register/activate/{hash}')
    configurator.add_route(name='password:reset', pattern='/password/reset')
    configurator.add_route(name='password:reset:continue', pattern='/password/reset/{hash}',
                           custom_predicates=(predicates.reset_hash,))
    configurator.add_route(name='email:change', pattern='/email/change')
    configurator.add_route(name='email:change:continue', pattern='/email/change/{hash}',
                           custom_predicates=(predicates.change_email_hash,))
    # scan base views
    configurator.scan('pyramid_fullauth.views.basic')

    # check for the social. If social is not available, we will not turn it on!
    if 'social' in fullauth_config:
        # Velruse init (for social auth)

        # scan social views
        configurator.scan('pyramid_fullauth.views.social')
        providers = fullauth_config.social
        configurator.registry['config']['login_providers'] = providers
        for provider in providers:
            # Ugly hack for using google oauth2, not OpenID + Oauth2 from google
            provider_settings = fullauth_config['social'][provider]
            if provider == 'google':  # pragma: no cover
                provider = 'google_oauth2'

            configurator.include('velruse.providers.' + provider)
            getattr(configurator, 'add_{0}_login'.format(provider))(**provider_settings)

    # we'll add some request methods:
    configurator.add_request_method(login_perform, name='login_perform')
    configurator.add_request_method(user, name='user', reify=True)

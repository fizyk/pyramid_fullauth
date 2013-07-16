# -*- coding: utf-8 -*-
import logging

from tzf.pyramid_yml import config_defaults
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig


from pyramid_fullauth.auth import groupfinder
from pyramid_fullauth.routing import predicates
from pyramid_fullauth.request import login_perform
from pyramid_fullauth.request import user

__version__ = '0.0.4'


logger = logging.getLogger(__name__)


def includeme(configurator):
    '''
    pyramid_fullauth includeme method

    :param pyramid.configurator.Configurator configurator: pyramid's configurator object
    '''

    config_defaults(configurator, 'pyramid_fullauth:config')

    configurator.set_authorization_policy(ACLAuthorizationPolicy())
    configurator.set_authentication_policy(AuthTktAuthenticationPolicy(callback=groupfinder,
                                                                       **configurator.registry['config'].fullauth.AuthTkt))

    configurator.set_session_factory(UnencryptedCookieSessionFactoryConfig('alternative.secret'))

    # add routes
    configurator.add_route(name='login', pattern='/login')
    configurator.add_route(name='logout', pattern='/logout')
    configurator.add_route(name='register', pattern='/register')
    configurator.add_route(name='register:activate', pattern='/register/activate/{hash}',
                           custom_predicates=(predicates.activate_hash,))
    configurator.add_route(name='password:reset', pattern='/password/reset')
    configurator.add_route(name='password:reset:continue', pattern='/password/reset/{hash}',
                           custom_predicates=(predicates.reset_hash,))
    configurator.add_route(name='email:change', pattern='/email/change')
    configurator.add_route(name='email:change:continue', pattern='/email/change/{hash}',
                           custom_predicates=(predicates.change_email_hash,))
    # scan base views
    configurator.scan('pyramid_fullauth.views.basic')

    # check for the social. If social is not available, we will not turn it on!
    if 'social' in configurator.registry['config'].fullauth:
        # Velruse init (for social auth)

        # scan social views
        configurator.scan('pyramid_fullauth.views.social')
        providers = configurator.registry['config'].fullauth.social
        configurator.registry['config']['login_providers'] = providers
        for provider in providers:
            # Ugly hack for using google oauth2, not OpenID + Oauth2 from google
            if provider == 'google':
                configurator.include('velruse.providers.google_oauth2')
                getattr(configurator, 'add_google_oauth2_login')(
                    **configurator.registry['config']['fullauth']['social'][provider])
            else:
                configurator.include('velruse.providers.' + provider)
                getattr(configurator, 'add_{0}_login'.format(provider))(
                    **configurator.registry['config']['fullauth']['social'][provider])

    # we'll add some request methods:
    configurator.add_request_method(login_perform, name='login_perform')
    configurator.add_request_method(user, name='user', reify=True)

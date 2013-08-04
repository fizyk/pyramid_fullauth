# -*- coding: utf-8 -*-

import unittest

from pyramid.view import view_config
from pyramid_basemodel import Session
import transaction
import lxml.html
import lxml.html.clean

try:
    from webtest import TestApp
except ImportError:
    raise ImportError("You need WebTest module!! (pip install WebTest)")


from pyramid_fullauth.models import User
from pyramid_fullauth.auth import BaseACLRootFactoryMixin


def config_factory(**settings):
    """Call with settings to make and configure a configurator instance.
    """
    from pyramid.config import Configurator
    from pyramid.session import UnencryptedCookieSessionFactoryConfig

    # Prepared tests for future use of pyramid_basemodel
    settings['sqlalchemy.url'] = 'sqlite:///:memory:'
    settings['basemodel.should_drop_all'] = True

    # Initialise the ``Configurator`` and setup a session factory.
    config = Configurator(settings=settings,
                          root_factory=BaseACLRootFactoryMixin)

    # Include the dependencies.
    config.include('pyramid_tm')
    config.include('pyramid_basemodel')
    config.include('tzf.pyramid_yml')
    config.include('pyramid_fullauth')

    config.add_route('secret', '/secret')
    config.scan('tests')

    # Return the configurator instance.
    return config


@view_config(route_name="secret", permission="super_high", renderer='json')
def secret_view(request):
    '''Dummy view with redirect to login'''
    return dict()


class BaseTestSuite(object):

    user_data = {
        'email': u'email@example.com',
        'password': u'Password',
        'address_ip': u'0.0.0.0',
    }

    def read_user(self, email):
        '''
            Reads user
        '''
        return Session.query(User).filter(User.email == email).first()

    def create_user(self, update_data=None):
        user = User(**self.user_data)
        Session.add(user)

        # Flush to put to the DB and generate defaults
        Session.flush()

        if update_data:
            for update in update_data.items():
                setattr(user, update[0], update[1])

        transaction.commit()

    def get_token(self, url, app):
        from lxml import etree
        res = app.get(url, status=200)
        node = etree.fromstring(res.body)
        token = node.xpath('//input[@name="token"]/@value')[0]
        return str(token)

    def authenticate(self, app, email=user_data['email'],
                     password=user_data['password'], token=None):
        """ Login user """
        if not token:
            token = self.get_token('/login?after=%2Fsecret', app)

        post_data = {
            'email': email,
            'password': password,
            'token': token
        }
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        app.post('/login', post_data, headers=headers)


class BaseTestCase(unittest.TestCase, BaseTestSuite):

    '''old class, to be removed, after migrated to py.test completely'''

    def setUp(self, settings={}):
        """Configure the Pyramid application."""

        settings['yml.location'] = 'tests:config'
        # Configure redirect routes
        self.config = config_factory(**settings)
        # Add routes for change_password, change_username,

        self.app = TestApp(self.config.make_wsgi_app())

    def tearDown(self):
        '''
            Tearing down tests
        '''
        Session.remove()

    def get_token(self, url):
        from lxml import etree
        res = self.app.get(url, status=200)
        node = etree.fromstring(res.body)
        token = node.xpath('//input[@name="token"]/@value')[0]
        return str(token)

    def authenticate(self, email=BaseTestSuite.user_data['email'],
                     password=BaseTestSuite.user_data['password'], token=None):
        """ Login user """
        if not token:
            token = self.get_token('/login?after=%2Fsecret')

        post_data = {
            'email': email,
            'password': password,
            'token': token
        }
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        self.app.post('/login', post_data, headers=headers)

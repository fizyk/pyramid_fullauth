# -*- coding: utf-8 -*-

import unittest

from pyramid.view import view_config

try:
    from webtest import TestApp
except ImportError:
    raise ImportError("You need WebTest module!! (pip install WebTest)")


def config_factory(**settings):
    """Call with settings to make and configure a configurator instance.
    """
    from pyramid.config import Configurator
    from pyramid.session import UnencryptedCookieSessionFactoryConfig

    # Prepared tests for future use of pyramid_basemodel
    settings['sqlalchemy.url'] = 'sqlite:///:memory:'
    settings['basemodel.should_drop_all'] = True

    # Initialise the ``Configurator`` and setup a session factory.
    config = Configurator(settings=settings)

    config.include('pyramid_fullauth')

    config.add_route('forbidden', '/forbidden')
    config.scan('tests')

    # Return the configurator instance.
    return config


@view_config(route_name="forbidden", permission="super_high", renderer='json')
def secret_view(request):
    '''Dummy view with redirect to login'''
    return dict()


class BaseTestCase(unittest.TestCase):

    def setUp(self, settings={}):
        """Configure the Pyramid application."""

        # Configure redirect routes
        self.config = config_factory(**settings)
        # Add routes for change_password, change_username,

        self.app = TestApp(self.config.make_wsgi_app())

    def tearDown(self):
        '''
            Tearing down tests
        '''


class ConfigTest(BaseTestCase):

    def test_defaults(self):
        '''Load defaults config for fullauth'''

        self.assertTrue('fullauth' in self.config.registry['config'],
                        'Config should get created based on fullauth defaults')

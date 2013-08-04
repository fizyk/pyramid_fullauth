import pytest
try:
    from webtest import TestApp
except ImportError:
    raise ImportError("You need WebTest module!! (pip install WebTest)")

from tests.utils import config_factory
from pyramid_basemodel import Session


class App(object):

    def __init__(self, app, config):
        self.app = app
        self.config = config


@pytest.fixture(scope='function')
def base_app(request):
    """Configure the Pyramid application."""

    # Configure redirect routes
    config = config_factory(**{'yml.location': 'tests:config'})
    # Add routes for change_password, change_username,

    app = TestApp(config.make_wsgi_app())

    request.addfinalizer(Session.remove)

    return App(app, config)


@pytest.fixture(scope='function')
def app_no_password_required(request):
    """Configure the Pyramid application."""

    # Configure redirect routes
    config = config_factory(**{'yml.location': 'tests:config',
                               'env': 'np'})
    # Add routes for change_password, change_username,

    app = TestApp(config.make_wsgi_app())

    request.addfinalizer(Session.remove)

    return App(app, config)


@pytest.fixture(scope='function')
def app_authable(request):
    """Configure the Pyramid application."""

    # Configure redirect routes
    config = config_factory(**{'yml.location': 'tests:config',
                               'env': 'login'})
    # Add routes for change_password, change_username,

    app = TestApp(config.make_wsgi_app())

    request.addfinalizer(Session.remove)

    return App(app, config)


@pytest.fixture(scope='function')
def app_no_password_confirm(request):
    """Configure the Pyramid application."""

    # Configure redirect routes
    config = config_factory(**{'yml.location': 'tests:config',
                               'env': 'pc'})
    # Add routes for change_password, change_username,

    app = TestApp(config.make_wsgi_app())

    request.addfinalizer(Session.remove)

    return App(app, config)

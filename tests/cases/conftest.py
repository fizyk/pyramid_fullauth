
from mock import Mock


try:
    from webtest import TestApp
except ImportError:
    raise ImportError("You need WebTest module!! (pip install WebTest)")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pyramid_fullauth.models import Base, User
from tests import config_factory
from pyramid_basemodel import Session


@pytest.fixture()
def web_request():
    request = Mock()

    def _(message, *args, **kwargs):
        return message
    request._ = Mock(side_effect=_)
    request.configure_mock(
        **{'config.fullauth.register.password':
            {'length_min': 8, 'confirm': True},
            'POST': {'confirm_password': '987654321'}
           }
    )

    return request


@pytest.fixture(scope='function')
def database(request):
    connection = 'sqlite://'

    engine = create_engine(connection, echo=False)

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    def destroy():
        Base.metadata.drop_all(engine)
        session.close()

    request.addfinalizer(destroy)

    return session


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

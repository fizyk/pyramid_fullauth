import re

import transaction
from pyramid.view import view_config
from pyramid_basemodel import Session

from pyramid_fullauth.models import User

try:
    from webtest import TestApp
except ImportError:
    raise ImportError("You need WebTest module!! (pip install WebTest)")


from pyramid_fullauth.models import User
from pyramid_fullauth.auth import BaseACLRootFactoryMixin

user_data = {
    'email': u'email@example.com',
    'password': u'Password',
    'address_ip': u'0.0.0.0',
}


def create_user(session, user_data=user_data):
    user = User(**user_data)
    session.add(user)
    transaction.commit()


def config_factory(**settings):
    """Call with settings to make and configure a configurator instance.
    """
    from pyramid.config import Configurator
    from pyramid.session import UnencryptedCookieSessionFactoryConfig

    # Prepared tests for future use of pyramid_basemodel
    settings['sqlalchemy.url'] = 'sqlite:///:memory:'
    settings['basemodel.should_drop_all'] = True

    settings['pyramid.includes'] = ['pyramid_tm', 'pyramid_basemodel']

    # Initialise the ``Configurator`` and setup a session factory.
    config = Configurator(settings=settings,
                          root_factory=BaseACLRootFactoryMixin)

    # Include the dependencies.
    config.include('tzf.pyramid_yml')
    config.include('pyramid_fullauth')

    config.add_route('secret', '/secret')
    config.scan('tests.utils')

    # Return the configurator instance.
    return config


@view_config(route_name="secret", permission="super_high", renderer='json')
def secret_view(request):
    '''Dummy view with redirect to login'''
    return dict()

token_re = re.compile('^.*name="csrf_token" value="([a-z0-9]+)".*$',
                      re.I + re.M + re.DOTALL)


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
        res = app.get(url, status=200)
        matches = token_re.search(res.body)
        return str(matches.groups()[0])

    def authenticate(self, app, email=user_data['email'],
                     password=user_data['password'], token=None):
        """ Login user """
        if not token:
            csrf_token = self.get_token('/login', app)

        post_data = {
            'email': email,
            'password': password,
            'csrf_token': csrf_token
        }
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        return app.post('/login', post_data, headers=headers)

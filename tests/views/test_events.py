"""All events related tests."""
import pytest

from pytest_pyramid import factories


from pyramid_fullauth.events import (
    BeforeLogIn, AlreadyLoggedIn
)
from tests.tools import authenticate, DEFAULT_USER


evented_config = factories.pyramid_config({
    'yml.location': 'tests:config',
    'env': 'login',
    'pyramid.includes': [
        'pyramid_tm',
        'pyramid_fullauth',
        'tests.tools.include_views',
        'tests.views.test_events.include_views'
    ]
})


from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound


def include_views(config):
    """Dummy pyramid plugin including events."""
    config.add_route('event', '/event')
    config.scan('tests.event_listeners')
    # config.add_subscriber(raise_attribute_error, BeforeLogIn)


@view_config(route_name="event", renderer='json')
def event_view(request):
    """Dummy view."""
    return {'event', request.GET.get('event')}


def redirect_to_secret(event):
    """Redirect to event page with event name set as query event attribute."""
    raise HTTPFound(
        event.request.route_path(
            'event', _query=(('event', event.__class__.__name__),)
        ))


@pytest.fixture
def alreadyloggedin_config(evented_config):
    """Add AlreadyLoggedIn event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, AlreadyLoggedIn)
    return evented_config

alreadyloggedin_app = factories.pyramid_app('alreadyloggedin_config')


def test_default_login_redirect_from_event(active_user, alreadyloggedin_app):
    """After successful login, access to login page should result in redirect."""
    authenticate(alreadyloggedin_app)
    res = alreadyloggedin_app.get('/login', status=302)
    assert res.location == 'http://localhost/event?event=AlreadyLoggedIn'


@pytest.fixture
def beforelogin_config(evented_config):
    """Add BeforeLogIn event that raises AttributeError with event class name."""
    def raise_attribute_error(event):
        """Raise attribute error with message being the event class name."""
        if event.user:
            raise AttributeError(event.__class__.__name__)
    evented_config.add_subscriber(raise_attribute_error, BeforeLogIn)
    return evented_config

beforelogin_app = factories.pyramid_app('beforelogin_config')


def test_error_beforelogin(active_user, beforelogin_app):
    """Test errors from BeforeLogIn event."""
    res = beforelogin_app.get('/login')
    post_data = {
        'email': DEFAULT_USER['email'],
        'password': DEFAULT_USER['password'],
        'csrf_token': res.form['csrf_token'].value
    }
    res = beforelogin_app.post('/login', post_data, xhr=True)
    assert res.json['status'] is False
    assert res.json['msg'] == 'BeforeLogIn'

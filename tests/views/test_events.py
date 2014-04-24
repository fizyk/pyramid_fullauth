"""All events related tests."""
import pytest
import transaction
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from sqlalchemy.orm.exc import NoResultFound
from pytest_pyramid import factories


from pyramid_fullauth.models import User
from pyramid_fullauth.events import (
    BeforeLogIn, AfterLogIn, AlreadyLoggedIn,
    BeforeEmailChange, AfterEmailChange, AfterEmailChangeActivation,
    BeforeReset, AfterResetRequest, AfterReset
)
from tests.tools import authenticate, is_user_logged, DEFAULT_USER

EVENT_PATH = '/event?event={0.__name__}'
EVENT_URL = 'http://localhost' + EVENT_PATH


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


def include_views(config):
    """Dummy pyramid plugin including events."""
    config.add_route('event', '/event')
    config.scan('tests.views.test_events')
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


def raise_attribute_error(event):
    """Raise attribute error with message being the event class name."""
    if event.user:
        raise AttributeError(event.__class__.__name__)


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
    assert res.location == EVENT_URL.format(AlreadyLoggedIn)


@pytest.fixture
def beforelogin_config(evented_config):
    """Add BeforeLogIn event that raises AttributeError with event class name."""
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


@pytest.fixture
def afterlogin_config(evented_config):
    """Add AfterLogIn event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, AfterLogIn)
    return evented_config

afterlogin_app = factories.pyramid_app('afterlogin_config')


def test_login_redirect(active_user, afterlogin_app):
    """Log in and test redirect from AfterLogIn."""
    assert is_user_logged(afterlogin_app) is False

    res = authenticate(afterlogin_app)
    assert res.location == EVENT_URL.format(AfterLogIn)

    assert is_user_logged(afterlogin_app) is True


@pytest.fixture
def afterloginerror_config(evented_config):
    """Add AfterLogIn event subscriber that raises AttributeError."""
    evented_config.add_subscriber(raise_attribute_error, AfterLogIn)
    return evented_config

afterloginerror_app = factories.pyramid_app('afterloginerror_config')


def test_error_afterlogin(active_user, afterloginerror_app):
    """Test errors from BeforeLogIn event."""
    res = afterloginerror_app.get('/login')
    post_data = {
        'email': DEFAULT_USER['email'],
        'password': DEFAULT_USER['password'],
        'csrf_token': res.form['csrf_token'].value
    }
    res = afterloginerror_app.post('/login', post_data, xhr=True)
    assert res.json['status'] is False
    assert res.json['msg'] == 'AfterLogIn'

    assert is_user_logged(afterloginerror_app) is False


@pytest.fixture
def beforeemailchange_config(evented_config):
    """Add BeforeEmailChange event subscriber that raises AttributeError."""
    evented_config.add_subscriber(raise_attribute_error, BeforeEmailChange)
    return evented_config

beforeemailchange_app = factories.pyramid_app('beforeemailchange_config')


def test_beforeemailchange_error(active_user, beforeemailchange_app):
    """Raise AttributeError from BeforeEmailChange event."""
    app = beforeemailchange_app

    authenticate(app)
    new_email = 'email@email.com'

    res = app.get('/email/change')
    res = app.post(
        '/email/change',
        {
            'csrf_token': res.form['csrf_token'].value,
            'email': new_email},
        xhr=True)
    assert res.json['status'] is False
    assert res.json['msg'] == 'BeforeEmailChange'


@pytest.fixture
def afteremailchange_config(evented_config):
    """Add AfterEmailChange, AfterEmailChangeActivation event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, AfterEmailChange)
    evented_config.add_subscriber(redirect_to_secret, AfterEmailChangeActivation)
    return evented_config

afteremailchange_app = factories.pyramid_app('afteremailchange_config')


def test_afteremailchange(db_session, active_user, afteremailchange_app):
    """Redirect after successful email change request."""
    app = afteremailchange_app

    authenticate(app)
    email = DEFAULT_USER['email']
    new_email = 'email@email.com'

    user = db_session.query(User).filter(User.email == email).one()

    res = app.get('/email/change')
    form = res.form
    form['email'] = new_email
    res = form.submit()
    assert res.location == EVENT_URL.format(AfterEmailChange)

    transaction.commit()

    user = db_session.query(User).filter(User.email == email).one()
    assert user.new_email == new_email
    assert user.email == email
    assert user.email_change_key is not None


def test_afteremailchange_xhr(db_session, active_user, afteremailchange_app):
    """Change email with valid data."""
    app = afteremailchange_app

    authenticate(app)
    email = DEFAULT_USER['email']
    new_email = 'email@email.com'

    user = db_session.query(User).filter(User.email == email).one()

    res = app.get('/email/change')
    res = app.post(
        '/email/change',
        {
            'csrf_token': res.form['csrf_token'].value,
            'email': new_email},
        xhr=True)
    assert res.json['status'] is True
    assert res.json['url'] == EVENT_PATH.format(AfterEmailChange)

    transaction.commit()

    user = db_session.query(User).filter(User.email == email).one()
    assert user.new_email == new_email
    assert user.email == email
    assert user.email_change_key is not None


def test_afteremailchangeactivation(db_session, active_user, afteremailchange_app):
    """Confirm email change view with redirect from AfterEmailChangeActivation."""
    app = afteremailchange_app
    # login user
    authenticate(app)

    email = DEFAULT_USER['email']
    user = db_session.query(User).filter(User.email == email).one()

    new_email = u'email2@email.com'
    user.set_new_email(new_email)
    transaction.commit()

    user = db_session.merge(user)
    res = app.get('/email/change/' + user.email_change_key)
    assert res.status_code == 302
    assert res.location == EVENT_URL.format(AfterEmailChangeActivation)

    with pytest.raises(NoResultFound):
        # there is no user with old email
        db_session.query(User).filter(User.email == email).one()

    user = db_session.query(User).filter(User.email == new_email).one()
    assert not user.email_change_key


@pytest.fixture
def afterreset_config(evented_config):
    """Add AfterReset, AfterResetRequest event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, AfterResetRequest)
    evented_config.add_subscriber(redirect_to_secret, AfterReset)
    return evented_config

afterreset_app = factories.pyramid_app('afterreset_config')


def test_afterresetrequest(user, db_session, afterreset_app):
    """Successful password reset request with redirect from AfterResetRequest."""
    user = db_session.merge(user)
    assert user.reset_key is None

    res = afterreset_app.get('/password/reset')
    res.form['email'] = user.email
    res = res.form.submit()
    assert res.location == EVENT_URL.format(AfterResetRequest)

    transaction.commit()

    user = db_session.query(User).filter(User.email == user.email).one()
    assert user.reset_key is not None


def test_afterreset(user, db_session, afterreset_app):
    """Actually change password with redirect from AfterReset."""
    user = db_session.merge(user)
    user.set_reset()
    transaction.commit()

    user = db_session.merge(user)
    res = afterreset_app.get('/password/reset/' + user.reset_key)

    res.form['password'] = 'YouShallPass'
    res.form['confirm_password'] = 'YouShallPass'
    res = res.form.submit()
    assert res.location == EVENT_URL.format(AfterReset)

    user = db_session.query(User).filter(User.email == user.email).one()
    assert user.reset_key is None
    assert user.check_password('YouShallPass') is True


@pytest.fixture
def beforereset_config(evented_config):
    """Add BeforeReset event subscriber that raises AttributeError."""
    evented_config.add_subscriber(raise_attribute_error, BeforeReset)
    return evented_config

beforereset_app = factories.pyramid_app('beforereset_config')


def test_beforereset(user, db_session, beforereset_app):
    """Error thrown from BeforeReset event."""
    user = db_session.merge(user)
    user.set_reset()
    transaction.commit()

    user = db_session.merge(user)
    res = beforereset_app.get('/password/reset/' + user.reset_key)

    res.form['password'] = 'YouShallPass'
    res.form['confirm_password'] = 'YouShallPass'
    res = res.form.submit()
    assert 'Error! BeforeReset' in res.body

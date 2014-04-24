"""All events related tests."""
import pytest
import transaction
from mock import MagicMock
from pyramid import testing
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from velruse import AuthenticationComplete
from sqlalchemy.orm.exc import NoResultFound
from pytest_pyramid import factories


from pyramid_fullauth.models import User
from pyramid_fullauth.views.social import SocialLoginViews
from pyramid_fullauth.events import (
    BeforeLogIn, AfterLogIn, AlreadyLoggedIn,
    BeforeEmailChange, AfterEmailChange, AfterEmailChangeActivation,
    BeforeReset, AfterResetRequest, AfterReset,
    AfterSocialRegister, AfterSocialLogIn, SocialAccountAlreadyConnected,
    AfterActivate,
    BeforeRegister, AfterRegister
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


@pytest.fixture
def aftersocialregister_config(evented_config):
    """Add AfterSocialRegister event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, AfterSocialRegister)
    return evented_config

aftersocialregister_app = factories.pyramid_app('aftersocialregister_config')


def test_aftersocialregister(aftersocialregister_config, aftersocialregister_app, db_session):
    """Register fresh user and logs him in and check response if redirect from AfterSocialRegister."""
    profile = {
        'accounts': [{'domain': u'facebook.com', 'userid': u'2343'}],
        'displayName': u'teddy',
        'verifiedEmail': u'we@po.pl',
        'preferredUsername': u'teddy',
        'emails': [{'value': u'aasd@bwwqwe.pl'}],
        'name': u'ted'
    }
    credentials = {'oauthAccessToken': '7897048593434'}
    provider_name = u'facebook'
    provider_type = u'facebook'
    request = testing.DummyRequest()
    request.user = None
    request.registry = aftersocialregister_config.registry
    request.remote_addr = u'127.0.0.123'
    request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)

    request.login_perform = MagicMock(name='login_perform')
    request.login_perform.return_value = {'status': True}
    view = SocialLoginViews(request)
    out = view()
    assert out.location == EVENT_PATH.format(AfterSocialRegister)
    transaction.commit()

    # read first new account
    user = db_session.query(User).one()
    assert user.is_active
    assert user.provider_id('facebook') == profile['accounts'][0]['userid']


@pytest.fixture
def aftersociallogin_config(evented_config):
    """Add AfterSocialLogIn event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, AfterSocialLogIn)
    return evented_config

aftersociallogin_app = factories.pyramid_app('aftersociallogin_config')


def test_aftersociallogin(aftersociallogin_config, aftersociallogin_app, db_session):
    """Register fresh user and logs him in and check response if redirect from AfterSocialLogIn."""
    profile = {
        'accounts': [{'domain': u'facebook.com', 'userid': u'2343'}],
        'displayName': u'teddy',
        'verifiedEmail': u'we@po.pl',
        'preferredUsername': u'teddy',
        'emails': [{'value': u'aasd@bwwqwe.pl'}],
        'name': u'ted'
    }
    credentials = {'oauthAccessToken': '7897048593434'}
    provider_name = u'facebook'
    provider_type = u'facebook'
    request = testing.DummyRequest()
    request.user = None
    request.registry = aftersociallogin_config.registry
    request.remote_addr = u'127.0.0.123'
    request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)

    def login_perform(*args, **kwargs):
        return HTTPFound(location=kwargs['location'])
    request.login_perform = login_perform
    view = SocialLoginViews(request)
    out = view()
    assert out.location == EVENT_PATH.format(AfterSocialLogIn)
    transaction.commit()

    # read first new account
    user = db_session.query(User).one()
    assert user.is_active
    assert user.provider_id('facebook') == profile['accounts'][0]['userid']


@pytest.fixture
def alreadyconnected_config(evented_config):
    """Add SocialAccountAlreadyConnected event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, SocialAccountAlreadyConnected)
    return evented_config

alreadyconnected_app = factories.pyramid_app('alreadyconnected_config')


def test_alreadyconnected(alreadyconnected_config, alreadyconnected_app, facebook_user, db_session):
    """Try to connect facebook account to logged in user used by other user check redirect from SocialAccountAlreadyConnected."""
    # this user will be logged and trying to connect facebook's user account.
    fresh_user = User(
        email='new@user.pl',
        password='somepassword',
        address_ip='127.0.0.1')
    db_session.add(fresh_user)
    transaction.commit()
    user = db_session.merge(facebook_user)
    fresh_user = db_session.merge(fresh_user)

    # mock request
    profile = {
        'accounts': [{'domain': u'facebook.com', 'userid': user.provider_id('facebook')}],
        'displayName': u'teddy',
        'preferredUsername': u'teddy',
        'emails': [{'value': u'aasd@basd.pl'}],
        'name': u'ted'
    }
    credentials = {'oauthAccessToken': '7897048593434'}
    provider_name = u'facebook'
    provider_type = u'facebook'
    request = testing.DummyRequest()
    request.user = fresh_user
    request.registry = alreadyconnected_config.registry
    request.remote_addr = u'127.0.0.123'
    request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)
    request._ = lambda msg, *args, **kwargs: msg

    request.login_perform = MagicMock(name='login_perform')
    request.login_perform.return_value = {'status': True}
    # call!
    view = SocialLoginViews(request)
    out = view()
    assert out.location == EVENT_PATH.format(SocialAccountAlreadyConnected)
    transaction.begin()
    fresh_user = db_session.merge(fresh_user)
    assert fresh_user.provider_id('facebook') is None


@pytest.fixture
def afteractivate_config(evented_config):
    """Add AfterActivate event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, AfterActivate)
    return evented_config

afteractivate_app = factories.pyramid_app('afteractivate_config')


def test_afteractivate(user, db_session, afteractivate_app):
    """Activate user adn check redirect through AfterActivate."""
    user = db_session.merge(user)

    res = afteractivate_app.get('/register/activate/' + user.activate_key)
    assert res.location == EVENT_URL.format(AfterActivate)
    transaction.commit()
    user = db_session.query(User).filter(User.email == user.email).one()

    assert not user.activate_key
    assert user.is_active
    assert user.activated_at

    authenticate(afteractivate_app)
    assert is_user_logged(afteractivate_app) is True


@pytest.fixture
def beforeregister_config(evented_config):
    """Add BeforeRegister event subscriber that raises AttributeError."""
    evented_config.add_subscriber(raise_attribute_error, BeforeRegister)
    return evented_config

beforeregister_app = factories.pyramid_app('beforeregister_config')


def test_beforeregister(db_session, beforeregister_app):
    """Register user check eror catching from BeforeRegister event."""
    assert db_session.query(User).count() == 0

    res = beforeregister_app.get('/register')
    res = beforeregister_app.post(
        '/register',
        {
            'csrf_token': res.form['csrf_token'].value,
            'email': 'test@test.co.uk',
            'password': 'passmeplease',
            'confirm_password': 'passmeplease'
        },
        extra_environ={'REMOTE_ADDR': '0.0.0.0'},
        xhr=True)
    assert res.json['errors']['msg'] == 'BeforeRegister'


@pytest.fixture
def afterregister_config(evented_config):
    """Add AfterRegister event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, AfterRegister)
    return evented_config

afteraregister_app = factories.pyramid_app('afterregister_config')


def test_afterregister(db_session, afteraregister_app):
    """Register user check eror catching from BeforeRegister event."""
    assert db_session.query(User).count() == 0
    email = 'test@test.co.uk'
    password = 'passmeplease'

    res = afteraregister_app.get('/register')
    res.form['email'] = email
    res.form['password'] = password
    res.form['confirm_password'] = password
    res = res.form.submit(extra_environ={'REMOTE_ADDR': '0.0.0.0'})
    assert res.location == EVENT_URL.format(AfterRegister)
    transaction.commit()

    user = db_session.query(User).filter(User.email == email).one()

    # User should not have active account at this moment
    assert user.is_active is not None
    assert user.check_password(password)

"""All events related tests."""

import http

import pytest
import transaction
from mock import MagicMock
from pyramid import testing
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pytest_pyramid import factories
from sqlalchemy.orm.exc import NoResultFound
from velruse import AuthenticationComplete

from pyramid_fullauth.events import (
    AfterActivate,
    AfterEmailChange,
    AfterEmailChangeActivation,
    AfterLogIn,
    AfterRegister,
    AfterReset,
    AfterResetRequest,
    AfterSocialLogIn,
    AfterSocialRegister,
    AlreadyLoggedIn,
    BeforeEmailChange,
    BeforeLogIn,
    BeforeRegister,
    BeforeReset,
    SocialAccountAlreadyConnected,
)
from pyramid_fullauth.models import User
from pyramid_fullauth.views.social import SocialLoginViews
from tests.tools import DEFAULT_USER, authenticate, is_user_logged
from tests.views.conftest import mock_translate

EVENT_PATH = "/event?event={0.__name__}"
EVENT_URL = "http://localhost" + EVENT_PATH


def unregister_subscriber(config, event):
    """Unregister subscribers from given events."""
    # pylint:disable=protected-access
    for key in config.registry.adapters._subscribers[1].keys():
        if key.implementedBy(event):
            del config.registry.adapters._subscribers[1][key]
            break


evented_config = factories.pyramid_config(
    settings={  # pylint:disable=invalid-name
        "env": "login",
        "fullauth.authtkt.timeout": 2,
        "fullauth.authtkt.reissue_time": 0.2,
        "fullauth.register.password.require": True,
        "fullauth.register.password.length_min": 8,
        "fullauth.register.password.confirm": True,
        "pyramid.includes": [
            "pyramid_tm",
            "pyramid_fullauth",
            "tests.tools.include_views",
            "tests.views.test_events.include_views",
        ],
    }
)


def include_views(config):
    """Configure pyramid to include test view and it's path."""
    config.add_route("event", "/event")
    config.scan("tests.views.test_events")


@view_config(route_name="event", renderer="json")
def event_view(request):
    """Return exactly received value."""
    return {"event", request.GET.get("event")}


def redirect_to_secret(event):
    """Redirect to event page with event name set as query event attribute."""
    raise HTTPFound(event.request.route_path("event", _query=(("event", event.__class__.__name__),)))


def raise_attribute_error(event):
    """Raise attribute error with message being the event class name."""
    if event.user:
        raise AttributeError(event.__class__.__name__)


@pytest.fixture
def alreadyloggedin_config(evented_config):  # pylint:disable=redefined-outer-name
    """Add AlreadyLoggedIn event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, AlreadyLoggedIn)
    evented_config.commit()
    yield evented_config
    unregister_subscriber(evented_config, AlreadyLoggedIn)


alreadyloggedin_app = factories.pyramid_app("alreadyloggedin_config")  # pylint:disable=invalid-name


@pytest.mark.usefixtures("active_user")
def test_default_login_redirect_from_event(
    alreadyloggedin_app,
):  # pylint:disable=redefined-outer-name
    """After successful login, access to login page should result in redirect."""
    authenticate(alreadyloggedin_app)
    res = alreadyloggedin_app.get("/login", status=http.HTTPStatus.FOUND)
    assert res.location == EVENT_URL.format(AlreadyLoggedIn)


@pytest.fixture
def beforelogin_config(evented_config):  # pylint:disable=redefined-outer-name
    """Add BeforeLogIn event that raises AttributeError with event class name."""
    evented_config.add_subscriber(raise_attribute_error, BeforeLogIn)
    evented_config.commit()
    yield evented_config
    unregister_subscriber(evented_config, BeforeLogIn)


beforelogin_app = factories.pyramid_app("beforelogin_config")  # pylint:disable=invalid-name


@pytest.mark.usefixtures("active_user")
def test_error_beforelogin(beforelogin_app):  # pylint:disable=redefined-outer-name
    """Test errors from BeforeLogIn event."""
    res = beforelogin_app.get("/login")
    post_data = {
        "email": DEFAULT_USER["email"],
        "password": DEFAULT_USER["password"],
        "csrf_token": res.form["csrf_token"].value,
    }
    res = beforelogin_app.post("/login", post_data, xhr=True)
    assert res.json["status"] is False
    assert res.json["msg"] == "BeforeLogIn"


@pytest.fixture
def afterlogin_config(evented_config):  # pylint:disable=redefined-outer-name
    """Add AfterLogIn event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, AfterLogIn)
    evented_config.commit()
    yield evented_config
    unregister_subscriber(evented_config, AfterLogIn)


afterlogin_app = factories.pyramid_app("afterlogin_config")  # pylint:disable=invalid-name


@pytest.mark.usefixtures("active_user")
def test_login_redirect(afterlogin_app):  # pylint:disable=redefined-outer-name
    """Log in and test redirect from AfterLogIn."""
    assert is_user_logged(afterlogin_app) is False

    res = authenticate(afterlogin_app)
    assert res.location == EVENT_URL.format(AfterLogIn)

    assert is_user_logged(afterlogin_app) is True


@pytest.fixture
def afterloginerror_config(evented_config):  # pylint:disable=redefined-outer-name
    """Add AfterLogIn event subscriber that raises AttributeError."""
    evented_config.add_subscriber(raise_attribute_error, AfterLogIn)
    evented_config.commit()
    yield evented_config
    unregister_subscriber(evented_config, AfterLogIn)


afterloginerror_app = factories.pyramid_app("afterloginerror_config")  # pylint:disable=invalid-name


@pytest.mark.usefixtures("active_user")
def test_error_afterlogin(afterloginerror_app):  # pylint:disable=redefined-outer-name
    """Test errors from BeforeLogIn event."""
    res = afterloginerror_app.get("/login")
    post_data = {
        "email": DEFAULT_USER["email"],
        "password": DEFAULT_USER["password"],
        "csrf_token": res.form["csrf_token"].value,
    }
    res = afterloginerror_app.post("/login", post_data, xhr=True)
    assert res.json["status"] is False
    assert res.json["msg"] == "AfterLogIn"

    assert is_user_logged(afterloginerror_app) is False


@pytest.fixture
def beforeemailchange_config(evented_config):  # pylint:disable=redefined-outer-name
    """Add BeforeEmailChange event subscriber that raises AttributeError."""
    evented_config.add_subscriber(raise_attribute_error, BeforeEmailChange)
    evented_config.commit()
    yield evented_config
    unregister_subscriber(evented_config, BeforeEmailChange)


beforeemailchange_app = factories.pyramid_app("beforeemailchange_config")  # pylint:disable=invalid-name


@pytest.mark.usefixtures("active_user")
def test_beforeemailchange_error(
    beforeemailchange_app,
):  # pylint:disable=redefined-outer-name
    """Raise AttributeError from BeforeEmailChange event."""
    app = beforeemailchange_app

    authenticate(app)
    new_email = "email@email.com"

    res = app.get("/email/change")
    res = app.post(
        "/email/change",
        {"csrf_token": res.form["csrf_token"].value, "email": new_email},
        xhr=True,
    )
    assert res.json["status"] is False
    assert res.json["msg"] == "BeforeEmailChange"


@pytest.fixture
def afteremailchange_config(evented_config):  # pylint:disable=redefined-outer-name
    """Add AfterEmailChange, AfterEmailChangeActivation event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, AfterEmailChange)
    evented_config.add_subscriber(redirect_to_secret, AfterEmailChangeActivation)
    evented_config.commit()
    yield evented_config
    unregister_subscriber(evented_config, AfterEmailChange)
    unregister_subscriber(evented_config, AfterEmailChangeActivation)


afteremailchange_app = factories.pyramid_app("afteremailchange_config")  # pylint:disable=invalid-name


@pytest.mark.usefixtures("active_user")
def test_afteremailchange(db_session, afteremailchange_app):  # pylint:disable=redefined-outer-name
    """Redirect after successful email change request."""
    app = afteremailchange_app

    authenticate(app)
    email = DEFAULT_USER["email"]
    new_email = "email@email.com"

    user = db_session.query(User).filter(User.email == email).one()

    res = app.get("/email/change")
    form = res.form
    form["email"] = new_email
    res = form.submit()
    assert res.location == EVENT_URL.format(AfterEmailChange)

    transaction.commit()

    user = db_session.query(User).filter(User.email == email).one()
    assert user.new_email == new_email
    assert user.email == email
    assert user.email_change_key is not None


@pytest.mark.usefixtures("active_user")
def test_afteremailchange_xhr(db_session, afteremailchange_app):  # pylint:disable=redefined-outer-name
    """Change email with valid data."""
    app = afteremailchange_app

    authenticate(app)
    email = DEFAULT_USER["email"]
    new_email = "email@email.com"

    user = db_session.query(User).filter(User.email == email).one()

    res = app.get("/email/change")
    res = app.post(
        "/email/change",
        {"csrf_token": res.form["csrf_token"].value, "email": new_email},
        xhr=True,
    )
    assert res.json["status"] is True
    assert res.json["url"] == EVENT_PATH.format(AfterEmailChange)

    transaction.commit()

    user = db_session.query(User).filter(User.email == email).one()
    assert user.new_email == new_email
    assert user.email == email
    assert user.email_change_key is not None


@pytest.mark.usefixtures("active_user")
def test_afteremailchangeactivation(db_session, afteremailchange_app):  # pylint:disable=redefined-outer-name
    """Confirm email change view with redirect from AfterEmailChangeActivation."""
    app = afteremailchange_app
    # login user
    authenticate(app)

    email = DEFAULT_USER["email"]
    user = db_session.query(User).filter(User.email == email).one()

    new_email = "email2@email.com"
    user.set_new_email(new_email)
    transaction.commit()

    user = db_session.merge(user)
    res = app.get("/email/change/" + user.email_change_key)
    assert res.status_code == http.HTTPStatus.FOUND
    assert res.location == EVENT_URL.format(AfterEmailChangeActivation)

    with pytest.raises(NoResultFound):
        # there is no user with old email
        db_session.query(User).filter(User.email == email).one()

    user = db_session.query(User).filter(User.email == new_email).one()
    assert not user.email_change_key


@pytest.fixture
def afterreset_config(evented_config):  # pylint:disable=redefined-outer-name
    """Add AfterReset, AfterResetRequest event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, AfterResetRequest)
    evented_config.add_subscriber(redirect_to_secret, AfterReset)
    evented_config.commit()
    yield evented_config
    unregister_subscriber(evented_config, AfterResetRequest)
    unregister_subscriber(evented_config, AfterReset)


afterreset_app = factories.pyramid_app("afterreset_config")  # pylint:disable=invalid-name


def test_afterresetrequest(user, db_session, afterreset_app):  # pylint:disable=redefined-outer-name
    """Successful password reset request with redirect from AfterResetRequest."""
    user = db_session.merge(user)
    assert user.reset_key is None

    res = afterreset_app.get("/password/reset")
    res.form["email"] = user.email
    res = res.form.submit()
    assert res.location == EVENT_URL.format(AfterResetRequest)

    transaction.commit()

    user = db_session.query(User).filter(User.email == user.email).one()
    assert user.reset_key is not None


def test_afterreset(user, db_session, afterreset_app):  # pylint:disable=redefined-outer-name
    """Actually change password with redirect from AfterReset."""
    user = db_session.merge(user)
    user.set_reset()
    transaction.commit()

    user = db_session.merge(user)
    res = afterreset_app.get("/password/reset/" + user.reset_key)

    res.form["password"] = "YouShallPass"
    res.form["confirm_password"] = "YouShallPass"
    res = res.form.submit()
    assert res.location == EVENT_URL.format(AfterReset)

    user = db_session.query(User).filter(User.email == user.email).one()
    assert user.reset_key is None
    assert user.check_password("YouShallPass") is True


@pytest.fixture
def beforereset_config(evented_config):  # pylint:disable=redefined-outer-name
    """Add BeforeReset event subscriber that raises AttributeError."""
    evented_config.add_subscriber(raise_attribute_error, BeforeReset)
    evented_config.commit()
    yield evented_config
    unregister_subscriber(evented_config, BeforeReset)


beforereset_app = factories.pyramid_app("beforereset_config")  # pylint:disable=invalid-name


def test_beforereset(user, db_session, beforereset_app):  # pylint:disable=redefined-outer-name
    """Error thrown from BeforeReset event."""
    user = db_session.merge(user)
    user.set_reset()
    transaction.commit()

    user = db_session.merge(user)
    res = beforereset_app.get("/password/reset/" + user.reset_key)

    res.form["password"] = "YouShallPass"
    res.form["confirm_password"] = "YouShallPass"
    res = res.form.submit()
    assert "Error! BeforeReset" in res.body.decode("unicode_escape")


@pytest.fixture
def aftersocialregister_config(evented_config):  # pylint:disable=redefined-outer-name
    """Add AfterSocialRegister event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, AfterSocialRegister)
    evented_config.commit()
    yield evented_config
    unregister_subscriber(evented_config, AfterSocialRegister)


aftersocialregister_app = factories.pyramid_app("aftersocialregister_config")  # pylint:disable=invalid-name


@pytest.mark.usefixtures("aftersocialregister_app")
def test_aftersocialregister(aftersocialregister_config, db_session):  # pylint:disable=redefined-outer-name
    """Register fresh user and logs him in and check response if redirect from AfterSocialRegister."""
    profile = {
        "accounts": [{"domain": "facebook.com", "userid": "2343"}],
        "displayName": "teddy",
        "verifiedEmail": "we@po.pl",
        "preferredUsername": "teddy",
        "emails": [{"value": "aasd@bwwqwe.pl"}],
        "name": "ted",
    }
    credentials = {"oauthAccessToken": "7897048593434"}
    provider_name = "facebook"
    provider_type = "facebook"
    request = testing.DummyRequest()
    request.user = None
    request.registry = aftersocialregister_config.registry
    request.remote_addr = "127.0.0.123"
    request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)

    request.login_perform = MagicMock(name="login_perform")
    request.login_perform.return_value = {"status": True}
    view = SocialLoginViews(request)
    out = view()
    assert out.location == EVENT_PATH.format(AfterSocialRegister)
    transaction.commit()

    # read first new account
    user = db_session.query(User).one()
    assert user.is_active
    assert user.provider_id("facebook") == profile["accounts"][0]["userid"]


@pytest.fixture
def aftersociallogin_config(evented_config):  # pylint:disable=redefined-outer-name
    """Add AfterSocialLogIn event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, AfterSocialLogIn)
    evented_config.commit()
    yield evented_config
    unregister_subscriber(evented_config, AfterSocialLogIn)


aftersociallogin_app = factories.pyramid_app("aftersociallogin_config")  # pylint:disable=invalid-name


@pytest.mark.usefixtures("aftersociallogin_app")
def test_aftersociallogin(aftersociallogin_config, db_session):  # pylint:disable=redefined-outer-name
    """Register fresh user and logs him in and check response if redirect from AfterSocialLogIn."""
    profile = {
        "accounts": [{"domain": "facebook.com", "userid": "2343"}],
        "displayName": "teddy",
        "verifiedEmail": "we@po.pl",
        "preferredUsername": "teddy",
        "emails": [{"value": "aasd@bwwqwe.pl"}],
        "name": "ted",
    }
    credentials = {"oauthAccessToken": "7897048593434"}
    provider_name = "facebook"
    provider_type = "facebook"
    request = testing.DummyRequest()
    request.user = None
    request.registry = aftersociallogin_config.registry
    request.remote_addr = "127.0.0.123"
    request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)

    def login_perform(*_, **kwargs):
        return HTTPFound(location=kwargs["location"])

    request.login_perform = login_perform
    view = SocialLoginViews(request)
    out = view()
    assert out.location == EVENT_PATH.format(AfterSocialLogIn)
    transaction.commit()

    # read first new account
    user = db_session.query(User).one()
    assert user.is_active
    assert user.provider_id("facebook") == profile["accounts"][0]["userid"]


@pytest.fixture
def alreadyconnected_config(evented_config):  # pylint:disable=redefined-outer-name
    """Add SocialAccountAlreadyConnected event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, SocialAccountAlreadyConnected)
    evented_config.commit()
    yield evented_config
    unregister_subscriber(evented_config, SocialAccountAlreadyConnected)


alreadyconnected_app = factories.pyramid_app("alreadyconnected_config")  # pylint:disable=invalid-name


@pytest.mark.usefixtures("alreadyconnected_app")
def test_alreadyconnected(alreadyconnected_config, facebook_user, db_session):  # pylint:disable=redefined-outer-name
    """Try to connect facebook account to logged in user used by other users facebook account.

    Check redirect from SocialAccountAlreadyConnected.
    """
    # this user will be logged and trying to connect facebook's user account.
    fresh_user = User(
        email="new@user.pl",
        password="somepassword",
        address_ip="127.0.0.1",
    )
    db_session.add(fresh_user)
    transaction.commit()
    user = db_session.merge(facebook_user)
    fresh_user = db_session.merge(fresh_user)

    # mock request
    profile = {
        "accounts": [
            {
                "domain": "facebook.com",
                "userid": user.provider_id("facebook"),
            }
        ],
        "displayName": "teddy",
        "preferredUsername": "teddy",
        "emails": [{"value": "aasd@basd.pl"}],
        "name": "ted",
    }
    credentials = {"oauthAccessToken": "7897048593434"}
    provider_name = "facebook"
    provider_type = "facebook"
    request = testing.DummyRequest()
    request.user = fresh_user
    request.registry = alreadyconnected_config.registry
    request.remote_addr = "127.0.0.123"
    request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)
    request._ = mock_translate

    request.login_perform = MagicMock(name="login_perform")
    request.login_perform.return_value = {"status": True}
    # call!
    view = SocialLoginViews(request)
    out = view()
    assert out.location == EVENT_PATH.format(SocialAccountAlreadyConnected)
    transaction.begin()
    fresh_user = db_session.merge(fresh_user)
    assert fresh_user.provider_id("facebook") is None


@pytest.fixture
def afteractivate_config(evented_config):  # pylint:disable=redefined-outer-name
    """Add AfterActivate event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, AfterActivate)
    evented_config.commit()
    yield evented_config
    unregister_subscriber(evented_config, AfterActivate)


afteractivate_app = factories.pyramid_app("afteractivate_config")  # pylint:disable=invalid-name


def test_afteractivate(user, db_session, afteractivate_app):  # pylint:disable=redefined-outer-name
    """Activate user adn check redirect through AfterActivate."""
    user = db_session.merge(user)

    res = afteractivate_app.get("/register/activate/" + user.activate_key)
    assert res.location == EVENT_URL.format(AfterActivate)
    transaction.commit()
    user = db_session.query(User).filter(User.email == user.email).one()

    assert not user.activate_key
    assert user.is_active
    assert user.activated_at

    authenticate(afteractivate_app)
    assert is_user_logged(afteractivate_app) is True


@pytest.fixture
def beforeregister_config(evented_config):  # pylint:disable=redefined-outer-name
    """Add BeforeRegister event subscriber that raises AttributeError."""
    evented_config.add_subscriber(raise_attribute_error, BeforeRegister)
    evented_config.commit()
    yield evented_config
    unregister_subscriber(evented_config, BeforeRegister)


beforeregister_app = factories.pyramid_app("beforeregister_config")  # pylint:disable=invalid-name


def test_beforeregister(db_session, beforeregister_app):  # pylint:disable=redefined-outer-name
    """Register user check eror catching from BeforeRegister event."""
    assert db_session.query(User).count() == 0

    res = beforeregister_app.get("/register")
    res = beforeregister_app.post(
        "/register",
        {
            "csrf_token": res.form["csrf_token"].value,
            "email": "test@test.co.uk",
            "password": "passmeplease",
            "confirm_password": "passmeplease",
        },
        extra_environ={"REMOTE_ADDR": "0.0.0.0"},
        xhr=True,
    )
    assert res.json["errors"]["msg"] == "BeforeRegister"


@pytest.fixture
def afterregister_config(evented_config):  # pylint:disable=redefined-outer-name
    """Add AfterRegister event subscriber that redirects to event page."""
    evented_config.add_subscriber(redirect_to_secret, AfterRegister)
    evented_config.commit()
    yield evented_config
    unregister_subscriber(evented_config, AfterRegister)


afteraregister_app = factories.pyramid_app("afterregister_config")  # pylint:disable=invalid-name


def test_afterregister(db_session, afteraregister_app):  # pylint:disable=redefined-outer-name
    """Register user check eror catching from BeforeRegister event."""
    assert db_session.query(User).count() == 0
    email = "test@test.co.uk"
    password = "passmeplease"

    res = afteraregister_app.get("/register")
    res.form["email"] = email
    res.form["password"] = password
    res.form["confirm_password"] = password
    res = res.form.submit(extra_environ={"REMOTE_ADDR": "0.0.0.0"})
    assert res.location == EVENT_URL.format(AfterRegister)
    transaction.commit()

    user = db_session.query(User).filter(User.email == email).one()

    # User should not have active account at this moment
    assert user.is_active is not None
    assert user.check_password(password)

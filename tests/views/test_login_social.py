"""Social network login test."""

from urllib.parse import parse_qs, urlparse

import transaction
from mock import MagicMock
from pyramid import testing
from velruse import AuthenticationComplete

from pyramid_fullauth.models import User
from pyramid_fullauth.views.social import SocialLoginViews
from tests.views.conftest import mock_translate


def test_social_login_link(social_app):
    """Login:Form displayed social form."""
    res = social_app.get("/login")
    assert "Connect with facebook</a>" in res.body.decode("unicode_escape")


def test_social_click_link(social_app):
    """Click social login link."""
    res = social_app.get("/login/facebook?scope=email%2Coffline_access", status=302)
    redirect = urlparse(res.headers["Location"])
    query = parse_qs(redirect.query)
    assert redirect.netloc == "www.facebook.com", "We should redirect user to facebook"
    assert redirect.path == "/dialog/oauth/", "Path should be oauth"
    assert "redirect_uri" in query
    assert "scope" in query
    assert query["redirect_uri"] == ["http://localhost/login/facebook/callback"]
    assert query["scope"] == ["email,offline_access"]


def test_social_login_register(social_config, db_session):
    """Register fresh user and logs him in."""
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
    request.registry = social_config.registry
    request.remote_addr = "127.0.0.123"
    request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)

    request.login_perform = MagicMock(name="login_perform")
    request.login_perform.return_value = {"status": True}
    view = SocialLoginViews(request)
    out = view()
    assert out == {"status": True}
    transaction.commit()

    # read first new account
    user = db_session.query(User).one()
    assert user.is_active
    assert user.provider_id("facebook") == profile["accounts"][0]["userid"]


def test_login_different_social_account(social_config, db_session, facebook_user):  # pylint:disable=unused-argument
    """Login with different social account than connected from same provider.

    System should let user in, but not change connection.
    """
    # profile mock response
    profile = {
        # facebook user id is different than user's
        "accounts": [{"domain": "facebook.com", "userid": "2343"}],
        "displayName": "teddy",
        "verifiedEmail": facebook_user.email,
        "preferredUsername": "teddy",
        "emails": [{"value": "aasd@bwwqwe.pl"}],
        "name": "ted",
    }
    request = testing.DummyRequest()
    request.user = None
    request.registry = social_config.registry
    request.remote_addr = "127.0.0.123"
    request.context = AuthenticationComplete(
        profile,
        {"oauthAccessToken": "7897048593434"},
        "facebook",
        "facebook",
    )

    request.login_perform = MagicMock(name="login_perform")
    request.login_perform.return_value = {"status": True}
    view = SocialLoginViews(request)
    out = view()
    # user should be authenticated recognized by email!
    assert out["status"] is True
    assert facebook_user.provider_id("facebook") is not profile["accounts"][0]["userid"]


def test_login_social_connect(social_config, active_user, db_session):
    """Connect and logs user in."""
    user = db_session.merge(active_user)

    profile = {
        "accounts": [{"domain": "facebook.com", "userid": "2343"}],
        "displayName": "teddy",
        "preferredUsername": "teddy",
        "emails": [{"value": user.email}],
        "name": "ted",
    }
    credentials = {"oauthAccessToken": "7897048593434"}
    provider_name = "facebook"
    provider_type = "facebook"
    user = None
    request = testing.DummyRequest()
    request.user = user
    request.registry = social_config.registry
    request.remote_addr = "127.0.0.123"
    request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)

    request.login_perform = MagicMock(name="login_perform")
    request.login_perform.return_value = {"status": True}
    view = SocialLoginViews(request)
    out = view()
    assert out == {"status": True}


def test_logged_social_connect_account(social_config, active_user, db_session):
    """Connect facebook account to logged in user."""
    user = db_session.merge(active_user)

    profile = {
        "accounts": [{"domain": "facebook.com", "userid": "2343"}],
        "displayName": "teddy",
        "preferredUsername": "teddy",
        "emails": [{"value": "aasd@basd.pl"}],
        "name": "ted",
    }
    credentials = {"oauthAccessToken": "7897048593434"}
    provider_name = "facebook"
    provider_type = "facebook"
    request = testing.DummyRequest()
    request.user = user
    request.registry = social_config.registry
    request.remote_addr = "127.0.0.123"
    request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)
    request._ = mock_translate

    request.login_perform = MagicMock(name="login_perform")
    request.login_perform.return_value = {"status": True}
    view = SocialLoginViews(request)
    out = view()
    assert out["status"] is True

    transaction.commit()
    user = db_session.merge(user)
    assert user.provider_id("facebook") == profile["accounts"][0]["userid"]


def test_logged_social_connect_self(social_config, facebook_user, db_session):
    """Connect self."""
    user = db_session.merge(facebook_user)

    profile = {
        "accounts": [
            {
                "domain": "facebook.com",
                "userid": user.provider_id("facebook"),
            }
        ],
        "displayName": "teddy",
        "preferredUsername": "teddy",
        "emails": [{"value": user.email}],
        "name": "ted",
    }
    credentials = {"oauthAccessToken": "7897048593434"}
    provider_name = "facebook"
    provider_type = "facebook"
    request = testing.DummyRequest()
    request.user = user
    request.registry = social_config.registry
    request.remote_addr = "127.0.0.123"
    request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)
    request._ = mock_translate

    request.login_perform = MagicMock(name="login_perform")
    request.login_perform.return_value = {"status": True}
    view = SocialLoginViews(request)
    out = view()
    assert out["status"] is True

    user = db_session.merge(facebook_user)
    assert user.provider_id("facebook") == profile["accounts"][0]["userid"]


def test_logged_social_connect_second_account(social_config, facebook_user, db_session):
    """Connect second facebook account to logged in user."""
    user = db_session.merge(facebook_user)

    # mock request
    profile = {
        "accounts": [{"domain": "facebook.com", "userid": "2343"}],
        "displayName": "teddy",
        "preferredUsername": "teddy",
        "emails": [{"value": "aasd@basd.pl"}],
        "name": "ted",
    }
    credentials = {"oauthAccessToken": "7897048593434"}
    provider_name = "facebook"
    provider_type = "facebook"
    request = testing.DummyRequest()
    request.user = user
    request.registry = social_config.registry
    request.remote_addr = "127.0.0.123"
    request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)
    request._ = mock_translate

    request.login_perform = MagicMock(name="login_perform")
    request.login_perform.return_value = {"status": True}
    view = SocialLoginViews(request)
    out = view()
    # status should be false
    assert out["status"] is False
    assert out["msg"] == "Your account is already connected to other ${provider} account."
    assert user.provider_id("facebook") is not profile["accounts"][0]["userid"]


def test_logged_social_connect_used_account(social_config, facebook_user, db_session):
    """Try to connect facebook account to logged in user used by other user."""
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
    request.registry = social_config.registry
    request.remote_addr = "127.0.0.123"
    request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)
    request._ = mock_translate

    request.login_perform = MagicMock(name="login_perform")
    request.login_perform.return_value = {"status": True}
    # call!
    view = SocialLoginViews(request)
    out = view()
    # status should be false
    assert out["status"] is False
    assert out["msg"] == "This ${provider} account is already connected with other account."
    transaction.begin()
    fresh_user = db_session.merge(fresh_user)
    assert fresh_user.provider_id("facebook") is None

"""Logout related tests."""

import http
import time

from tests.tools import authenticate, is_user_logged


def test_logout(active_user, extended_app):  # pylint:disable=unused-argument
    """Check logout action."""
    authenticate(extended_app)
    assert is_user_logged(extended_app) is True

    extended_app.get("/logout", status=http.HTTPStatus.SEE_OTHER)
    assert is_user_logged(extended_app) is False
    res = extended_app.get("/secret", status=http.HTTPStatus.FOUND)
    assert res.status_code == http.HTTPStatus.FOUND


def test_logout_login(active_user, extended_config, extended_app):  # pylint:disable=unused-argument
    """Check logout action with configured logout redirection."""
    extended_config.registry["fullauth"]["redirects"]["logout"] = "login"
    authenticate(extended_app)
    assert is_user_logged(extended_app) is True

    res = extended_app.get("/logout", status=http.HTTPStatus.SEE_OTHER)
    assert is_user_logged(extended_app) is False
    # redirection should be done to login page.
    assert "/login" in res.location
    res = extended_app.get("/secret", status=http.HTTPStatus.FOUND)
    assert res.status_code == http.HTTPStatus.FOUND


def test_automatic_logout(active_user, short_config, short_app):  # pylint:disable=unused-argument
    """Test automatic logout."""
    timeout = short_config.registry["fullauth"]["authtkt"]["timeout"] + 1

    authenticate(short_app)
    # Simulating inactivity
    time.sleep(timeout)
    res = short_app.get("/email/change")
    assert res.headers["Location"] == "http://localhost/login?after=%2Femail%2Fchange"
    res = res.follow()
    assert res.form

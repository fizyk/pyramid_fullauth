"""Logout related tests."""
import time

from tests.tools import authenticate, is_user_logged


def test_logout(active_user, extended_app):
    """Check logout action."""
    authenticate(extended_app)
    assert is_user_logged(extended_app) is True

    extended_app.get('/logout', status=303)
    assert is_user_logged(extended_app) is False
    res = extended_app.get('/secret', status=302)
    assert res.status_code == 302


def test_logout_login(active_user, extended_config, extended_app):
    """Check logout action with configured logout redirection."""
    extended_config.registry['config'].fullauth.redirects.logout = 'login'
    authenticate(extended_app)
    assert is_user_logged(extended_app) is True

    res = extended_app.get('/logout', status=303)
    assert is_user_logged(extended_app) is False
    # redirection should be done to login page.
    assert '/login' in res.location
    res = extended_app.get('/secret', status=302)
    assert res.status_code == 302


def test_automatic_logout(active_user, short_config, short_app):
    """Test automatic logout."""
    timeout = short_config.registry['config']['fullauth']['AuthTkt']['timeout'] + 1

    authenticate(short_app)
    # Simulating inactivity
    time.sleep(timeout)
    res = short_app.get('/email/change')
    assert res.headers['Location'] == 'http://localhost/login?after=%2Femail%2Fchange'
    res = res.follow()
    assert res.form

"""Log in related test."""
import time

import pytest
from tests.tools import authenticate, is_user_logged, DEFAULT_USER


def test_login_view(default_app):
    """Login view."""
    res = default_app.get('/login')
    assert res.form
    assert 'email' in res.form.fields
    assert 'password' in res.form.fields
    assert 'remember' in res.form.fields


def test_login_view_secret(extended_app):
    """Login:Form displayed after redirect from protected view."""
    res = extended_app.get('/secret', status=302)
    # check if redirect is correct
    assert res.headers['Location'] == 'http://localhost/login?after=%2Fsecret'
    # redirecting
    res = extended_app.get(res.headers['Location'])
    assert res.form
    assert 'email' in res.form.fields


def test_login(active_user, extended_app):
    """Actually log in test."""
    res = extended_app.get('/secret', status=302)
    assert res
    res = extended_app.get('/login?after=%2Fsecret')

    assert is_user_logged(extended_app) is False

    res = authenticate(extended_app)
    assert 'Max-Age=' not in str(res)

    assert is_user_logged(extended_app) is True


def test_login_xhr(active_user, default_app):
    """Test login in throu xhr request."""
    # get login page (csrf_token there)
    res = default_app.get('/login')

    # construct post data
    auth_data = {
        'csrf_token': res.form['csrf_token'].value,
        'email': DEFAULT_USER['email'],
        'password': DEFAULT_USER['password']
    }

    # send xhr request
    res = default_app.post('/login', auth_data, xhr=True)
    # make sure user is logged!
    assert is_user_logged(default_app) is True
    assert res.json['status'] is True
    assert res.json['after'] == '/'


def test_login_remember(active_user, extended_app):
    """Login user and mark remember me field."""
    res = extended_app.get('/login')
    assert is_user_logged(extended_app) is False

    res = authenticate(extended_app, remember=True)

    assert is_user_logged(extended_app) is True
    assert 'Max-Age=' in str(res)


def test_login_inactive(user, extended_app):
    """Log in inactive user."""
    assert is_user_logged(extended_app) is False

    authenticate(extended_app)

    assert is_user_logged(extended_app) is True


def test_login_redirects(active_user, extended_app):
    """Login with redirects."""
    res = extended_app.get('/secret', status=302)
    assert res.status_code == 302
    res = res.follow()
    res.form['email'] = DEFAULT_USER['email']
    res.form['password'] = DEFAULT_USER['password']
    res = res.form.submit()

    assert is_user_logged(extended_app) is True
    assert res.status_code == 302


@pytest.mark.parametrize('user_kwargs', (
    {'password': 'wrong password'},
    {'email': 'not@registered.py'}
))
def test_login_wrong(active_user, user_kwargs, extended_app):
    """Use wrong password during authentication."""
    res = authenticate(extended_app, response_code=200, **user_kwargs)

    assert 'Error! Wrong e-mail or password.' in res
    assert res


@pytest.mark.parametrize('post_data', (
    {
        'email': DEFAULT_USER['email'],
        'password': DEFAULT_USER['password'],
    }, {
        'email': DEFAULT_USER['email'],
        'password': DEFAULT_USER['password'],
        'csrf_token': '8934798289723789347892397832789432789'
    }

))
def test_login_csrf_error(active_user, extended_app, post_data):
    """Try to log in with erroneus csrf token."""
    res = extended_app.get('/login', status=200)
    assert res
    res = extended_app.post('/login', post_data, status=401)

    assert is_user_logged(extended_app) is False


def test_logout(active_user, extended_app):
    """Check logout action."""
    authenticate(extended_app)
    assert is_user_logged(extended_app) is True

    extended_app.get('/logout', status=302)
    assert is_user_logged(extended_app) is False
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


def test_login_success_xhr(active_user, extended_app):
    """Test xhr authentication."""
    res = extended_app.get('/login')
    post_data = {
        'email': DEFAULT_USER['email'],
        'password': DEFAULT_USER['password'],
        'csrf_token': res.form['csrf_token'].value
    }
    extended_app.get('/secret', status=302)
    res = extended_app.post('/login?after=%2Fsecret',
                            post_data,
                            xhr=True,
                            expect_errors=True)

    assert res.content_type == 'application/json'
    assert is_user_logged(extended_app) is True
    assert res.json['status']


def test_default_login_forbidden(active_user, authable_app):
    """After successful login, user should get 403 on secret page."""
    authenticate(authable_app)
    authable_app.get('/secret', status=403)


def test_default_login_redirectaway(active_user, authable_app):
    """After successful login, access to login page should result in redirect."""
    authenticate(authable_app)
    authable_app.get('/login', status=302)

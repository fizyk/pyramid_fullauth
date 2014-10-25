"""Log in related test."""
import pytest
import transaction

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


@pytest.mark.parametrize('email', (
    DEFAULT_USER['email'].lower(),
    DEFAULT_USER['email'].upper()
))
def test_login_ok(active_user, extended_app, email):
    """Actually log in test."""
    res = extended_app.get('/secret', status=302)
    res = res.follow()
    res = extended_app.get('/login?after=%2Fsecret')

    assert is_user_logged(extended_app) is False

    res = authenticate(extended_app, email=email)
    assert 'Max-Age=' not in str(res)

    assert is_user_logged(extended_app) is True


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
    assert res.status_code == 303


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
    assert res.json['status'] is True
    assert 'after' in res.json
    assert is_user_logged(extended_app) is True

    # second call
    res = extended_app.post('/login?after=%2Fsecret',
                            post_data,
                            xhr=True,
                            expect_errors=True)
    assert res.json['status'] is True
    assert res.json['msg'] == 'Already logged in!'


def test_default_login_forbidden(active_user, authable_app):
    """After successful login, user should get 403 on secret page."""
    authable_app.get('/secret', status=302)
    forbidden = authable_app.get('/secret', xhr=True, status=403)
    assert forbidden.json['status'] is False
    authenticate(authable_app)
    authable_app.get('/secret', status=403)
    # go back to secret page
    forbidden = authable_app.get('/secret', xhr=True, status=403)
    # no permission, but logged.
    assert forbidden.json['status'] is False
    assert 'login_url' not in forbidden.json


def test_default_login_redirectaway(active_user, authable_app):
    """After successful login, access to login page should result in redirect."""
    authenticate(authable_app)
    res = authable_app.get('/login', status=303)
    assert res.location == 'http://localhost/'


def test_login_invalid_cookie(db_session, active_user, extended_app):
    """Test access login page by deleted user."""
    res = authenticate(extended_app)
    assert 'Max-Age=' not in str(res)

    assert is_user_logged(extended_app) is True

    db_session.delete(active_user)
    transaction.commit()

    # will rise Attribute error
    res = extended_app.get('/login')
    assert res.status_code == 200, "Should stay since user is no longer valid!"

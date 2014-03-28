import time

import pytest
from tests.tools import authenticate, is_user_logged, DEFAULT_USER


def test_login_view(default_app):
    '''Login:Form displayed'''

    res = default_app.get('/login')
    assert res.form
    assert 'email' in res.form.fields
    assert 'password' in res.form.fields
    assert 'remember' in res.form.fields


def test_login_view_secret(extended_app):
    '''Login:Form displayed after redirect'''
    res = extended_app.get('/secret', status=302)
    # check if redirect is correct
    assert res.headers['Location'] == 'http://localhost/login?after=%2Fsecret'
    # redirecting
    res = extended_app.get(res.headers['Location'])
    assert res.form
    assert 'email' in res.form.fields


def test_login(active_user, extended_app):
    '''Login:Action test with clicks'''

    res = extended_app.get('/secret', status=302)
    assert res
    res = extended_app.get('/login?after=%2Fsecret')

    assert is_user_logged(extended_app) == False

    res = authenticate(extended_app)
    assert 'Max-Age=' not in str(res)

    assert is_user_logged(extended_app) == True


def test_login_remember(active_user, extended_app):
    '''Login:Action test with clicks'''

    res = extended_app.get('/login')
    assert is_user_logged(extended_app) == False

    res = authenticate(extended_app, remember=True)

    assert is_user_logged(extended_app) == True
    assert 'Max-Age=' in str(res)


def test_login_inactive(user, extended_app):
    """Login:Action test with clicks if user is inactive"""

    assert is_user_logged(extended_app) == False

    authenticate(extended_app)

    assert is_user_logged(extended_app) == True


def test_login_redirects(active_user, extended_app):
    '''Login:Action test send post simply'''

    res = extended_app.get('/secret', status=302)
    assert res.status_code == 302
    res = res.follow()
    res.form['email'] = DEFAULT_USER['email']
    res.form['password'] = DEFAULT_USER['password']
    res = res.form.submit()

    assert is_user_logged(extended_app) == True
    assert res.status_code == 302


def test_login_wrong(active_user, extended_app):
    """Login:Action test: wrong password"""
    res = authenticate(
        extended_app, password="wrong password", response_code=200)

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
    """Login:Action test: no csrf token"""

    res = extended_app.get('/login', status=200)
    assert res
    res = extended_app.post('/login', post_data, status=401)

    assert is_user_logged(extended_app) == False


def test_logout(active_user, extended_app):
    '''Logout:Action test'''

    authenticate(extended_app)
    assert is_user_logged(extended_app) == True

    extended_app.get('/logout', status=302)
    assert is_user_logged(extended_app) == False
    res = extended_app.get('/secret', status=302)
    assert res.status_code == 302


def test_automatic_logout(active_user, short_config, short_app):
    ''' Test user logged out after
        defined period of inactivity
    '''

    timeout = short_config.registry['config']['fullauth']['AuthTkt']['timeout'] + 1

    authenticate(short_app)
    # Simulating inactivity
    time.sleep(timeout)
    res = short_app.get('/email/change')
    assert res.headers['Location'] == 'http://localhost/login?after=%2Femail%2Fchange'
    res = res.follow()
    assert res.form


def test_automatic_logout_not_expired(active_user, short_config, short_app):
    ''' Test user not logged out,
        timeout did not expire
    '''
    timeout = short_config.registry['config']['fullauth']['AuthTkt']['timeout'] - 1

    authenticate(short_app)
    # Simulating inactivity
    time.sleep(timeout)
    res = short_app.get('/email/change')
    assert res.status_code == 200
    assert res.form


def test_login_success_xhr(active_user, extended_app):

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
    assert is_user_logged(extended_app) == True
    assert res.json['status']


def test_default_login_noredirect(active_user, authable_app):

    authres = authenticate(authable_app)
    res = authres.goto('/secret', status=403)
    assert res
    res = authres.goto('/login')
    assert res
    assert '<form id="login_form"' in res.body
    res = authres.goto('/secret', status=403)
    assert res

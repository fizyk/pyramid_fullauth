"""Tools used for fullauth tests."""
from pyramid.view import view_config
from pyramid.compat import text_type

DEFAULT_USER = {
    'username': text_type('u1'),
    'password': text_type('password1'),
    'email': text_type('email@example.com'),
    'address_ip': text_type('127.0.0.1')
}


def authenticate(app, email=DEFAULT_USER['email'],
                 password=DEFAULT_USER['password'],
                 remember=False,
                 response_code=303):
    """Authenticate user."""
    res = app.get('/login')
    form = res.form

    form['email'] = email
    form['password'] = password
    if remember:
        form['remember'] = 1

    res = form.submit()

    # We've been redirected after log in
    assert res.status_code == response_code

    return res


def is_user_logged(app):
    """Check for auth_tkt cookies beeing set to see if user is logged in."""
    cookies = app.cookies
    if 'auth_tkt' in cookies and cookies['auth_tkt']:

        return True
    return False

# this below are additional views crafted for tests.


def include_views(config):
    """Dummy pyramid 'plugin' adding dummy secret view."""
    config.add_route('secret', '/secret')
    config.scan('tests.tools')


@view_config(route_name="secret", permission="super_high", renderer='json')
def secret_view(request):
    """Dummy view with redirect to login."""
    return {}

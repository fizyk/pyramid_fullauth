from pyramid.view import view_config

DEFAULT_USER = {
    'username': 'u1',
    'password': 'password1',
    'email': 'email@example.com',
    'address_ip': '127.0.0.1'
}


def authenticate(app, email=DEFAULT_USER['email'],
                 password=DEFAULT_USER['password'],
                 remember=False,
                 response_code=302):
    """ Login user """

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
    '''
    Checks for auth_tkt cookies beeing set
    '''
    cookies = app.cookies
    if 'auth_tkt' in cookies and cookies['auth_tkt']:

        return True
    return False


def include_views(config):
    config.add_route('secret', '/secret')
    config.scan('tests.tools')


@view_config(route_name="secret", permission="super_high", renderer='json')
def secret_view(request):
    '''Dummy view with redirect to login'''
    return dict()

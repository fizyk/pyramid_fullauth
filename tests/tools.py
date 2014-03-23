DEFAULT_USER = {
    'username': 'u1',
    'password': 'password1',
    'email': 'email@example.com',
    'address_ip': '127.0.0.1'
}


def authenticate(app, email=DEFAULT_USER['email'],
                 password=DEFAULT_USER['password'], token=None):
    """ Login user """

    res = app.get('/login')
    form = res.form

    form['email'] = email
    form['password'] = password

    res = form.submit()

    # We've been redirected after log in
    assert res.status_code == 302

    return res

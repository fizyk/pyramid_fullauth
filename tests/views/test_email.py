from tests.tools import authenticate


def test_email_view_not_logged(default_app):
    '''Change Email:view user not logged in'''
    app = default_app
    res = app.get('/email/change')
    assert res.status_code == 302
    assert res.location == 'http://localhost/login?after=%2Femail%2Fchange'


def test_email_view_logged(db_session, user, default_app):
    '''Change Email:view user logged in'''
    app = default_app
    user = db_session.merge(user)
    user.is_active = True
    db_session.commit()
    # Session are de-syncronised

    # login user
    authenticate(app)

    res = app.get('/email/change')
    assert res.status_code == 200
    assert '<input type="email" placeholder="username@hostname.com" name="email" id="change[email]"/>' in res

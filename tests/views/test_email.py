import pytest
import transaction

from sqlalchemy.orm.exc import NoResultFound
from pyramid_fullauth.models import User

from tests.tools import authenticate, DEFAULT_USER


def test_email_view_not_logged(default_app):
    '''Change Email:view user not logged in'''
    app = default_app
    res = app.get('/email/change')
    assert res.status_code == 302
    assert res.location == 'http://localhost/login?after=%2Femail%2Fchange'


def test_email_view_logged(db_session, active_user, default_app):
    '''Change Email:view user logged in'''
    app = default_app
    db_session.close()
    # Session are de-syncronised

    # login user
    authenticate(app)

    res = app.get('/email/change')
    assert res.status_code == 200
    assert '<input type="email" placeholder="username@hostname.com" name="email" id="change[email]"/>' in res


def test_email_valid_view(db_session, active_user, default_app):
    '''Change Email:view Valid data'''
    app = default_app

    authenticate(app)
    email = DEFAULT_USER['email']
    new_email = 'email@email.com'

    user = db_session.query(User).filter(User.email == email).one()

    res = app.get('/email/change')
    form = res.form
    form['email'] = new_email
    res = form.submit()
    assert res

    transaction.commit()

    user = db_session.query(User).filter(User.email == email).one()
    assert user.new_email == new_email
    assert user.email == email
    assert user.email_change_key is not None


def test_email_wrong_email_view(
        db_session, active_user, default_app, invalid_email):
    '''Change Email:view Wrong email'''
    app = default_app
    # login user
    authenticate(app)

    email = DEFAULT_USER['email']
    user = db_session.query(User).filter(User.email == email).one()

    res = app.get('/email/change')
    form = res.form
    form['email'] = invalid_email
    res = form.submit()
    assert 'Error! Incorrect e-mail format' in res


def test_email_proceed(db_session, active_user, default_app):
    '''Change Email:changing email'''
    app = default_app
    # login user
    authenticate(app)

    email = DEFAULT_USER['email']
    user = db_session.query(User).filter(User.email == email).one()

    new_email = u'email2@email.com'
    user.set_new_email(new_email)
    transaction.commit()

    user = db_session.merge(user)
    res = app.get(str('/email/change/' + user.email_change_key))
    assert res.status == '302 Found'

    with pytest.raises(NoResultFound):
        # there is no user with old email
        db_session.query(User).filter(User.email == email).one()

    user = db_session.query(User).filter(User.email == new_email).one()
    assert not user.email_change_key

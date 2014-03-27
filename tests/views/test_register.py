from HTMLParser import HTMLParser

import transaction
import pytest

from pyramid_fullauth.models import User
from tests.tools import DEFAULT_USER


def test_register_view(default_app):
    '''Register:Form displayed'''
    res = default_app.get('/register')
    assert res.form


@pytest.mark.parametrize('email, password', (
    # casual
    (DEFAULT_USER['email'], DEFAULT_USER['password']),
    # loooong password
    (DEFAULT_USER['email'], DEFAULT_USER['password'] * 10000),
))
def test_register_success(db_session, default_app, email, password):
    '''
        Register:Register user
    '''
    assert db_session.query(User).count() == 0

    res = default_app.get('/register')
    res.form['email'] = email
    res.form['password'] = password
    res.form['confirm_password'] = password
    res = res.form.submit(extra_environ={'REMOTE_ADDR': '0.0.0.0'})
    transaction.commit()

    user = db_session.query(User).filter(User.email == email).one()

    # User should not have active account at this moment
    assert not user.is_active is None
    assert user.check_password(password)


def test_register_user_exists(db_session, user, default_app):
    '''
        Register:Register user Second try
    '''

    res = default_app.get('/register')
    res.form['email'] = DEFAULT_USER['email']
    res.form['password'] = DEFAULT_USER['password']
    res.form['confirm_password'] = DEFAULT_USER['password']
    res = res.form.submit(extra_environ={'REMOTE_ADDR': '0.0.0.0'})
    transaction.commit()

    assert 'User with given e-mail already exists' in res.body


@pytest.mark.parametrize('email, password, confirm_password, error', (
    # no email
    (None, DEFAULT_USER['password'], DEFAULT_USER['password'],
        'E-mail is empty'),
    # empty email
    ('', DEFAULT_USER['password'], DEFAULT_USER['password'],
        'E-mail is empty'),
    # not matching passwords
    (DEFAULT_USER['email'], DEFAULT_USER['password'], DEFAULT_USER['password'] + 'Typo',
        'Passwords don\'t match'),
    # long, incorect email
    (u'email' * 100 + '@wap.pl', DEFAULT_USER['password'], DEFAULT_USER['password'],
        'Incorrect e-mail format'),
    # too short password
    (DEFAULT_USER['email'], '12', '12',
        'Password is too short'),
    # empty password
    (DEFAULT_USER['email'], '', '', 'Please enter your password'),
))
def test_register_error(db_session, default_app, email, password, confirm_password, error):
    '''
        Register:Register user with errors
    '''
    assert db_session.query(User).count() == 0

    res = default_app.get('/register')
    if email is not None:
        res.form['email'] = email
    res.form['password'] = password
    res.form['confirm_password'] = confirm_password
    res = res.form.submit(extra_environ={'REMOTE_ADDR': '0.0.0.0'})
    transaction.commit()

    assert error in HTMLParser().unescape(res.body)
    assert db_session.query(User).count() == 0


def test_register_wrong_csrf(db_session, default_app):
    '''
        Register:Register user: Wrong csrf
    '''
    assert db_session.query(User).count() == 0

    res = default_app.get('/register')
    res.form['email'] = DEFAULT_USER['email']
    res.form['password'] = DEFAULT_USER['password']
    res.form['confirm_password'] = DEFAULT_USER['password']
    res.form['csrf_token'] = 'wrong_token'
    res = res.form.submit(extra_environ={'REMOTE_ADDR': '0.0.0.0'},
                          status=401)
    transaction.commit()

    assert db_session.query(User).count() == 0


def test_no_pass_confirm(db_session, nopassconfirm_app):
    '''
        Register: Register without password confirm option
    '''
    '''
        Register:Register user
    '''
    assert db_session.query(User).count() == 0

    res = nopassconfirm_app.get('/register')
    res.form['email'] = DEFAULT_USER['email']
    res.form['password'] = DEFAULT_USER['password']
    res = res.form.submit(extra_environ={'REMOTE_ADDR': '0.0.0.0'})

    assert not 'Passwords don\'t match!' in HTMLParser().unescape(res.body)
    transaction.commit()

    user = db_session.query(User).filter(User.email == DEFAULT_USER['email']).one()

    # User should not have active account at this moment
    assert not user.is_active is None
    assert user.check_password(DEFAULT_USER['password'])

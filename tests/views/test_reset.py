"""Reset password views."""
try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser

import transaction
from pyramid.compat import text_type

from pyramid_fullauth.models import User

NEW_PASSWORD = 'YouShallPass'


def test_reset_view(default_app):
    """Simple get test."""
    res = default_app.get('/password/reset')
    assert res.form


def test_reset_action(user, db_session, default_app):
    """Successful password reset request."""
    user = db_session.merge(user)
    assert user.reset_key is None

    res = default_app.get('/password/reset')
    res.form['email'] = user.email
    res = res.form.submit()

    transaction.commit()

    user = db_session.query(User).filter(User.email == user.email).one()
    assert user.reset_key is not None


def test_reset_email_not_exists(user, db_session, default_app):
    """Reset password request with wrong email (not in database)."""
    user = db_session.merge(user)

    res = default_app.get('/password/reset')
    res.form['email'] = text_type('wrong@example.com')
    res = res.form.submit()
    assert 'Error! User does not exist' in res


def test_reset_proceed(user, db_session, default_app):
    """Actually change password."""
    user = db_session.merge(user)
    user.set_reset()
    transaction.commit()

    user = db_session.merge(user)
    res = default_app.get('/password/reset/' + user.reset_key)
    assert 'Recover your password - choose new password' in res

    res.form['password'] = NEW_PASSWORD
    res.form['confirm_password'] = NEW_PASSWORD
    res = res.form.submit()

    user = db_session.query(User).filter(User.email == user.email).one()
    assert user.reset_key is None
    assert user.check_password(NEW_PASSWORD) is True


def test_reset_proceed_wrong_reset_key(user, db_session, default_app):
    """Try changing password with wrong reset_key."""
    user = db_session.merge(user)
    user.set_reset()
    transaction.commit()

    user = db_session.merge(user)
    res = default_app.get(
        '/password/reset/' + user.reset_key + 'randomchars', status=404)
    assert res.status_code == 404


def test_reset_proceed_wrong_confirm(user, db_session, default_app):
    """Reset test for reseting pasword with notmatched passwords."""
    user = db_session.merge(user)
    user.set_reset()
    transaction.commit()

    user = db_session.merge(user)
    res = default_app.get('/password/reset/' + user.reset_key)

    res.form['password'] = NEW_PASSWORD
    res.form['confirm_password'] = NEW_PASSWORD + 'Typo'
    res = res.form.submit()

    assert 'Error! Password doesn\'t match' in HTMLParser().unescape(res.body.decode('unicode_escape'))


def test_reset_proceed_wrong_csrf(user, db_session, default_app):
    """Reset test for reseting pasword with notmatched csrf."""
    user = db_session.merge(user)
    user.set_reset()
    transaction.commit()

    user = db_session.merge(user)
    res = default_app.get('/password/reset/' + user.reset_key)

    res.form['password'] = NEW_PASSWORD
    res.form['confirm_password'] = NEW_PASSWORD
    res.form['csrf_token'] = 'sadasere723612dassdgaSDs7a'
    res.form.submit(status=401)

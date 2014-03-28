from HTMLParser import HTMLParser
import transaction

from pyramid_fullauth.models import User

NEW_PASSWORD = 'YouShallPass'


def test_reset_view(default_app):
    '''Reset:view'''
    res = default_app.get('/password/reset')
    assert res.form


def test_reset_action(user, db_session, default_app):
    '''Reset:Request Action get reset code'''
    user = db_session.merge(user)
    assert user.reset_key is None

    res = default_app.get('/password/reset')
    res.form['email'] = user.email
    res = res.form.submit()

    transaction.commit()

    user = db_session.query(User).filter(User.email == user.email).one()
    assert user.reset_key is not None


def test_reset_email_not_exists(user, db_session, default_app):
    '''Reset:Request Action with wrong email'''
    user = db_session.merge(user)

    res = default_app.get('/password/reset')
    res.form['email'] = u'wrong@example.com'
    res = res.form.submit()
    assert 'Error! User does not exists' in res


def test_reset_proceed(user, db_session, default_app):
    '''Reset test for reseting pasword'''
    user = db_session.merge(user)
    user.set_reset()
    transaction.commit()

    user = db_session.merge(user)
    res = default_app.get(str('/password/reset/' + user.reset_key))
    assert 'Recover your password - choose new password' in res

    res.form['password'] = NEW_PASSWORD
    res.form['confirm_password'] = NEW_PASSWORD
    res = res.form.submit()

    user = db_session.query(User).filter(User.email == user.email).one()
    assert user.reset_key is None
    assert user.check_password(NEW_PASSWORD) is True


def test_reset_proceed_wrong_confirm(user, db_session, default_app):
    '''Reset test for reseting pasword with notmatched passwords'''
    user = db_session.merge(user)
    user.set_reset()
    transaction.commit()

    user = db_session.merge(user)
    res = default_app.get(str('/password/reset/' + user.reset_key))

    res.form['password'] = NEW_PASSWORD
    res.form['confirm_password'] = NEW_PASSWORD + 'Typo'
    res = res.form.submit()

    assert 'Error! Password doesn\'t match' in HTMLParser().unescape(res.body)


def test_reset_proceed_wrong_csrf(user, db_session, default_app):
    '''Reset test for reseting pasword with notmatched csrf'''
    user = db_session.merge(user)
    user.set_reset()
    transaction.commit()

    user = db_session.merge(user)
    res = default_app.get(str('/password/reset/' + user.reset_key))

    res.form['password'] = NEW_PASSWORD
    res.form['confirm_password'] = NEW_PASSWORD
    res.form['csrf_token'] = 'sadasere723612dassdgaSDs7a'
    res.form.submit(status=401)

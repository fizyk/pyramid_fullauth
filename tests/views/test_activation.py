# -*- coding: utf-8 -*-
"""Account activation related tests."""
from urllib import quote

import transaction

from pyramid_fullauth.models import User
from tests.tools import authenticate, is_user_logged


def test_account_activation(user, db_session, default_app):
    """Activate user."""
    user = db_session.merge(user)

    default_app.get('/register/activate/' + user.activate_key)
    transaction.commit()
    user = db_session.query(User).filter(User.email == user.email).one()

    assert not user.activate_key
    assert user.is_active
    assert user.activated_at

    authenticate(default_app)
    assert is_user_logged(default_app) is True


def test_account_activation_wrong_key(user, db_session, default_app):
    """Activate user with wrong key."""
    user = db_session.merge(user)
    activate_key = user.activate_key
    res = default_app.get('/register/activate/' + activate_key[:-5], status=200)
    transaction.commit()

    assert 'Invalid activation code' in res.body

    user = db_session.query(User).filter(User.email == user.email).one()
    assert user.activate_key == activate_key
    assert user.activate_key is not None
    assert not user.activated_at
    # User should not have active account at this moment
    assert not user.is_active


def test_account_activation_key_with_trash_chars(user, db_session, default_app):
    """Strange characters in activation key."""
    user = db_session.merge(user)

    activate_key = user.activate_key
    res = default_app.get('/register/activate/' + quote(
        u'ąśðłĸęł¶→łęóħó³→←śðđ[]}³½ĸżćŋðń→↓ŧ¶ħ→ĸł¼²³↓←ħ@ĸđśðĸ@ł¼ęłśħđó[³²½łðśđħ'.encode('utf-8')),
        status=200
    )
    transaction.commit()

    assert 'Invalid activation code' in res.body
    user = db_session.query(User).filter(User.email == user.email).one()

    assert user.activate_key == activate_key
    assert user.activate_key is not None
    assert not user.activated_at
    # User should not have active account at this moment
    assert not user.is_active


def test_account_activation_twice(user, db_session, default_app):
    """Click activation link twice."""
    user = db_session.merge(user)

    activate_key = user.activate_key
    res = default_app.get('/register/activate/' + activate_key)
    transaction.commit()
    user = db_session.query(User).filter(User.email == user.email).one()

    assert not user.activate_key
    assert user.is_active
    assert user.activated_at

    res = default_app.get('/register/activate/' + activate_key, status=200)
    assert 'Invalid activation code' in res.body

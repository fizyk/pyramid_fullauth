# -*- coding: utf-8 -*-
"""Account activation related tests."""
try:
    from urllib import quote
    # python3
except ImportError:
    from urllib.parse import quote

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

    assert 'Invalid activation code' in res.body.decode('unicode_escape')

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
    res = default_app.get(
        '/register/activate/' + quote(
            # ąśðłĸęł¶→łęóħó³→←śðđ[]}³½ĸżćŋðń→↓ŧ¶ħ→ĸł¼²³↓←ħ@ĸđśðĸ@ł¼ęłśħđó[³²½łðśđħ - already decoded
            '\xc4\x85\xc5\x9b\xc3\xb0\xc5\x82\xc4\xb8\xc4\x99\xc5\x82\xc2\xb6\xe2\x86\x92\xc5\x82\xc4\x99\xc3\xb3\xc4\xa7\xc3\xb3\xc2\xb3\xe2\x86\x92\xe2\x86\x90\xc5\x9b\xc3\xb0\xc4\x91[]}\xc2\xb3\xc2\xbd\xc4\xb8\xc5\xbc\xc4\x87\xc5\x8b\xc3\xb0\xc5\x84\xe2\x86\x92\xe2\x86\x93\xc5\xa7\xc2\xb6\xc4\xa7\xe2\x86\x92\xc4\xb8\xc5\x82\xc2\xbc\xc2\xb2\xc2\xb3\xe2\x86\x93\xe2\x86\x90\xc4\xa7@\xc4\xb8\xc4\x91\xc5\x9b\xc3\xb0\xc4\xb8@\xc5\x82\xc2\xbc\xc4\x99\xc5\x82\xc5\x9b\xc4\xa7\xc4\x91\xc3\xb3[\xc2\xb3\xc2\xb2\xc2\xbd\xc5\x82\xc3\xb0\xc5\x9b\xc4\x91\xc4\xa7'  #noqa
        ),
        status=200
    )
    transaction.commit()

    assert 'Invalid activation code' in res.body.decode('unicode_escape')
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
    assert 'Invalid activation code' in res.body.decode('unicode_escape')

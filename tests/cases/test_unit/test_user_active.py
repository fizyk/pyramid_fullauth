import pytest

from pyramid.compat import text_type

from pyramid_fullauth.models import User
from tests.utils import create_user


def test_is_active_error():
    '''Is active can only be modified on object in session!'''

    with pytest.raises(AttributeError):
        user = User()
        user.is_active = True


def test_is_active(db):
    '''User:is_active'''
    create_user(db)

    user = db.query(User).filter(User.email == text_type('email@example.com')).one()
    assert not user.is_active
    assert not user.activated_at
    user.is_active = True
    assert user.is_active
    assert user.activated_at
    assert not user.deactivated_at
    user.is_active = False
    assert not user.is_active
    assert user.deactivated_at

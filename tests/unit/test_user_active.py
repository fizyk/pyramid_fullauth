import pytest

from pyramid_fullauth.models import User


def test_is_active_error():
    '''Is active can only be modified on object in session!'''

    with pytest.raises(AttributeError):
        user = User()
        user.is_active = True


def test_is_active(db_session, user):
    '''User:is_active'''
    user = db_session.merge(user)

    assert not user.is_active
    assert not user.activated_at
    user.is_active = True
    assert user.is_active
    assert user.activated_at
    assert not user.deactivated_at
    user.is_active = False
    assert not user.is_active
    assert user.deactivated_at

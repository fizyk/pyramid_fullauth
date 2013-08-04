import pytest
from pyramid.compat import text_type

from pyramid_fullauth.models import User
from pyramid_fullauth.exceptions import DeleteException
from tests.utils import create_user


def test_regular_user_not_admin(db_with_user):
    '''Regular user is_admin flag test
    '''

    user = db_with_user.query(User).filter(User.username == text_type('u1')).one()
    # Default user should not be an admin
    assert not user.is_admin


def test_remove_last_admin(db_with_user):
    '''Admin user is_admin flag test'''

    user = db_with_user.query(User).filter(User.username == text_type('u1')).one()
    user.is_admin = True
    db_with_user.commit()

    with pytest.raises(AttributeError):
        user.is_admin = False


def test_delete_admin(db_with_user):
    '''Admin user soft delete'''

    user = db_with_user.query(User).filter(User.email == text_type('email@example.com')).one()
    create_user(db_with_user, {'email': text_type('test2@example.com'),
                               'address_ip': '127.0.0.1',
                               'password': 'pass',
                               'is_admin': True})

    user.is_admin = True
    db_with_user.commit()

    user.delete()

    assert user.deleted_at


def test_delete_last_admin(db_with_user):
    '''Admin user soft delete'''

    user = db_with_user.query(User).filter(User.email == text_type('email@example.com')).one()

    user.is_admin = True
    db_with_user.commit()

    with pytest.raises(DeleteException):
        user.delete()

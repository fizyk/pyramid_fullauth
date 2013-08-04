import pytest
from pyramid.compat import text_type

from pyramid_fullauth.models import User
from pyramid_fullauth.exceptions import EmptyError


def test_hash_checkout(db_with_user):
    '''User::check_password()'''

    user = db_with_user.query(User).filter(User.username == text_type('u1')).one()
    assert user.check_password(text_type('password1'))


def test_hash_checkout_bad(db_with_user):
    '''User::check_password() False'''

    user = db_with_user.query(User).filter(User.username == text_type('u1')).one()
    assert not user.check_password(text_type('password2'))


@pytest.mark.parametrize('password', ['haselko', 'haselko' * 1000])
def test_password_change(db_with_user, password):
    '''User::password change'''

    new_password = text_type(password)

    user = db_with_user.query(User).filter(User.username == text_type('u1')).one()
    old_password = user.password
    old_salt = user._salt
    user.password = new_password
    db_with_user.commit()

    user = db_with_user.query(User).filter(User.username == text_type('u1')).one()
    assert not user.password == old_password
    assert not user._salt == old_salt
    assert user.check_password(new_password)


def test_password_empty(db_with_user):
    '''User::empty password change'''

    user = db_with_user.query(User).filter(User.username == text_type('u1')).one()

    with pytest.raises(EmptyError):
        user.password = text_type('')


def test_set_reset(db_with_user):
    '''User::set_reset()'''

    user = db_with_user.query(User).filter(User.username == text_type('u1')).one()
    assert not user.reset_key
    user.set_reset()
    assert user.reset_key

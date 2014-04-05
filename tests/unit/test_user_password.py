"""Password related user model behaviour."""
import pytest
from pyramid.compat import text_type
import transaction

from pyramid_fullauth.models import User
from pyramid_fullauth.exceptions import EmptyError


def test_hash_checkout(db_session, user):
    """User.check_password correct one."""
    user = db_session.merge(user)
    assert user.check_password(text_type('password1')) is True


def test_hash_checkout_bad(db_session, user):
    """User.check_password() wrong password."""
    user = db_session.merge(user)
    assert user.check_password(text_type('password2')) is False


@pytest.mark.parametrize('password', ['haselko', 'haselko' * 1000])
def test_password_change(db_session, user, password):
    """User password change."""
    new_password = text_type(password)

    user = db_session.merge(user)
    old_password = user.password
    old_salt = user._salt
    user.password = new_password
    transaction.commit()

    user = db_session.query(User).filter(User.username == text_type('u1')).one()
    assert not user.password == old_password
    assert not user._salt == old_salt
    assert user.check_password(new_password)


def test_password_empty(db_session, user):
    """User try to set empty password."""
    user = db_session.merge(user)

    with pytest.raises(EmptyError):
        user.password = text_type('')


def test_set_reset(db_session, user):
    """User.set_reset - generates reset key for those who forgot their password. """
    user = db_session.merge(user)
    assert not user.reset_key
    user.set_reset()
    assert user.reset_key

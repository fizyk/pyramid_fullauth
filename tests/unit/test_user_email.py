"""Test email related User methods."""
from pyramid.compat import text_type
from pyramid_fullauth.models import User

NEW_EMAIL = text_type('new@example.com')


def test_set_new_email():
    """
    Test User.set_new_email method.

    setting new email should result in setting new_email field,
    and key used to activate the change.
    """
    user = User()
    assert user.email_change_key is None
    assert user.new_email is None
    user.set_new_email(NEW_EMAIL)

    assert user.new_email == NEW_EMAIL
    assert user.email_change_key


def test_change_email():
    """
    Test User.change_email method.

    Calling it should copy new email set by set_new_email method
    into regular email field.
    """
    user = User()
    assert not user.email
    user.set_new_email(NEW_EMAIL)
    user.change_email()

    assert not user.email_change_key
    assert user.email == NEW_EMAIL

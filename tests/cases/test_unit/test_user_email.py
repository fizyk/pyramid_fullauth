import pytest
from pyramid.compat import text_type

from pyramid_fullauth.models import User


def test_set_new_email(db_with_user):
    '''User::set_new_email'''
    user = db_with_user.query(User).filter(User.email == text_type('email@example.com')).one()
    user.set_new_email(text_type('new@example.com'))

    assert user.email_change_key


def test_change_email(db_with_user):
    '''User::change_email'''
    user = db_with_user.query(User).filter(User.email == text_type('email@example.com')).one()
    user.set_new_email(text_type('new@example.com'))
    user.change_email()

    assert not user.email_change_key

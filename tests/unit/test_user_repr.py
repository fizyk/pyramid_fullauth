"""Test user representation."""
from pyramid.compat import text_type

from pyramid_fullauth.models import User


def test_introduce_email():
    """user gets introduced by e-mail only."""
    user = User()
    user.email = text_type('test@test.pl')
    # To string should return concatenated email
    assert str(user) == 'test@...'


def test_introduce_username():
    """user gets introduced by username."""
    user = User()
    # 'User not saved should be represented by \'None\'')
    assert str(user) == 'None'
    user.id = 1
    # if id is set, user should be presented with it
    assert str(user) == '1'

    user.email = text_type('test@test.pl')
    user.username = text_type('testowy')
    # To string should return username
    assert str(user) == 'testowy'
    # User should be represented by "<User (\'1\', \'testowy\')>"
    assert user.__repr__() == "<User ('1', 'testowy')>"

"""Test user representation."""

from pyramid_fullauth.models import User


def test_introduce_email():
    """User gets introduced by e-mail only."""
    user = User()
    user.email = "test@test.pl"
    # To string should return concatenated email
    assert str(user) == "test@..."


def test_introduce_username():
    """User gets introduced by username."""
    user = User()
    # 'User not saved should be represented by \'None\'')
    assert str(user) == "None"
    user.id = 1
    # if id is set, user should be presented with it
    assert str(user) == "1"

    user.email = "test@test.pl"
    user.username = "testowy"
    # To string should return username
    assert str(user) == "testowy"
    # User should be represented by "<User (\'1\')>"
    assert repr(user) == "<User ('1')>"

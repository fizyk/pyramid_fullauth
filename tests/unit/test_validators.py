"""Test various validators present on User class."""
import pytest
import transaction
from pyramid.compat import text_type

from pyramid_fullauth.models import User
from pyramid_fullauth.exceptions import EmptyError, EmailValidationError


@pytest.mark.parametrize('email', [
    text_type('very.common@example.com'),
    text_type('a.little.lengthy.but.fine@dept.example.com'),
    text_type('disposable.style.email.with+symbol@example.com'),
    text_type('"very.unusual.@.unusual.com"@example.com'),
    text_type('!#$%&\'*+-/=?^_`{}|~@example.org'),
    text_type('""@example.org'),
    text_type('"much.more unusual"@example.com'),
    text_type('"()<>[]:,;@\\\"!#$%&\'*+-/=?^_`{}| ~  ? ^_`{}|~.a"@example.org'),
])
def test_email_valid_formats(db_session, user, email):
    """Check all valid formats of Email (RFC 5321) can be set by user."""
    user = db_session.merge(user)

    user.email = email
    transaction.commit()

    user = db_session.query(User).filter(
        User.username == text_type('u1')).one()
    assert user.email == email


def test_email_empty(user):
    """Test reaction of email validator for empty email."""
    with pytest.raises(EmptyError):
        user.email = text_type('')


def test_email_invalid_formats(db_session, user, invalid_email):
    """Check all invalid formats of Email (RFC 5321) can not be set by user."""
    user = db_session.merge(user)

    with pytest.raises(EmailValidationError):
        user.email = invalid_email
        db_session.commit()

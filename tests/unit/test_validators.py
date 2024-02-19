"""Test various validators present on User class."""

import pytest
import transaction

from pyramid_fullauth.exceptions import EmailValidationError, EmptyError
from pyramid_fullauth.models import User


@pytest.mark.parametrize(
    "email",
    [
        "very.common@example.com",
        "a.little.lengthy.but.fine@dept.example.com",
        "disposable.style.email.with+symbol@example.com",
        '"very.unusual.@.unusual.com"@example.com',
        "!#$%&'*+-/=?^_`{}|~@example.org",
        '""@example.org',
        '"much.more unusual"@example.com',
        '"()<>[]:,;@\\"!#$%&\'*+-/=?^_`{}| ~  ? ^_`{}|~.a"@example.org',
    ],
)
def test_email_valid_formats(db_session, user, email):
    """Check all valid formats of Email (RFC 5321) can be set by user."""
    user = db_session.merge(user)

    user.email = email
    transaction.commit()

    user = db_session.query(User).filter(User.username == "u1").one()
    assert user.email == email


def test_email_empty(user):
    """Test reaction of email validator for empty email."""
    with pytest.raises(EmptyError):
        user.email = ""


def test_email_invalid_formats(db_session, user, invalid_email):
    """Check all invalid formats of Email (RFC 5321) can not be set by user."""
    user = db_session.merge(user)

    with pytest.raises(EmailValidationError):
        user.email = invalid_email
        transaction.commit()

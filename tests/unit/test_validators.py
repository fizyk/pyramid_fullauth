import pytest
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
    """Check all valid formats of Email (RFC 5321) can be set by user"""

    user = db_session.merge(user)

    user.email = email
    db_session.commit()

    user = db_session.query(User).filter(
        User.username == text_type('u1')).one()
    assert user.email == email


def test_email_empty(user):
    '''Test reaction of email validator for empty email'''

    with pytest.raises(EmptyError):
        user.email = text_type('')


@pytest.mark.parametrize('email', [
    # (an @ character must separate the local and domain parts)
    text_type('Abc.example.com'),
    # (character dot(.) is last in local part)
    text_type('Abc.@example.com'),
    # (character dot(.) is double)
    text_type('Abc..123@example.com'),
    # (only one @ is allowed outside quotation marks)
    text_type('A@b@c@example.com'),
    # (none of the special characters in this local part is allowed outside quotation marks)
    text_type('a"b(c)d,e:f;g<h>i[j\k]l@example.com'),
    # (quoted strings must be dot separated, or the only element making up the local-part)
    text_type('just"not"right@example.com'),
    # (spaces, quotes, and backslashes may only exist when within quoted strings and preceded by a backslash)
    text_type('this is"not\allowed@example.com'),
    # (even if escaped (preceded by a backslash), spaces, quotes, and backslashes must still be contained by quotes)
    text_type('this\ still\"not\\allowed@example.com'),
    text_type('bad-mail'),
])
def test_email_invalid_formats(db_session, user, email):
    '''
    Check all invalid formats of Email (RFC 5321) can not be set by user
    '''

    user = db_session.merge(user)

    with pytest.raises(EmailValidationError):
        user.email = email
        db.commit()

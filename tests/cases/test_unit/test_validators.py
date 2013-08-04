import pytest
from pyramid.compat import text_type
from pyramid_fullauth.models import User
from pyramid_fullauth.exceptions import EmptyError, EmailValidationError


class TestUserValidates(object):

    user_data = {'password': text_type('password1'),
                 'email': text_type('test@example.com'),
                 'address_ip': text_type('32.32.32.32')}

    def create_user(self, session, **user_data):
        '''method to create basic user'''
        user = User()

        for key in self.user_data:
            if not key in user_data:
                user_data[key] = self.user_data[key]

        for key in user_data:
            setattr(user, key, user_data[key])

        session.add(user)
        session.commit()

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
    def test_email_valid_formats(self, db, email):
        ''' Check all valid formats of Email (RFC 5321) can be set by user
        '''
        self.create_user(db, username=text_type('u1'))

        user = db.query(User).filter(User.username == text_type('u1')).one()

        user.email = email
        db.commit()

        user = db.query(User).filter(
            User.username == text_type('u1')).one()
        assert user.email == email

    def test_email_empty(self):
        '''Test reaction of email validator for empty email'''
        user = User()

        with pytest.raises(EmptyError):
            user.email = text_type('')

    @pytest.mark.parametrize('email', [
        'Abc.example.com'  # (an @ character must separate the local and domain parts)
        'Abc.@example.com'  # (character dot(.) is last in local part)
        'Abc..123@example.com'  # (character dot(.) is double)
        'A@b@c@example.com'  # (only one @ is allowed outside quotation marks)
        'a"b(c)d,e:f;g<h>i[j\k]l@example.com'  # (none of the special characters in this local part is allowed outside quotation marks)
        'just"not"right@example.com'  # (quoted strings must be dot separated, or the only element making up the local-part)
        'this is"not\allowed@example.com'  # (spaces, quotes, and backslashes may only exist when within quoted strings and preceded by a backslash)
        'this\ still\"not\\allowed@example.com'  # (even if escaped (preceded by a backslash), spaces, quotes, and backslashes must still be contained by quotes)
    ])
    def test_email_invalid_formats(self, db, email):
        '''
        Check all invalid formats of Email (RFC 5321) can not be set by user
        '''

        self.create_user(db, username=text_type('u1'))

        user = db.query(User).filter(User.username == text_type('u1')).one()
        assert user.email == text_type('test@example.com')

        with pytest.raises(EmailValidationError):
            user.email = email
            db.commit()

    def test_validate_email_bad(self):
        '''User::validate e-mail::bad'''

        user = User()
        with pytest.raises(EmailValidationError):
            user.email = text_type('bad-mail')

    def test_validate_email_ok(self):
        '''User::validate e-mail::ok'''

        user = User()
        email = text_type('test@test.info')
        user.email = email
        assert user.email == email

import pytest
from pyramid_fullauth.tools import validate_passsword, password_generator
from pyramid_fullauth.exceptions import (
    EmptyPasswordError, ShortPasswordError, PasswordConfirmMismatchError
)


class TestTools(object):

    @pytest.mark.parametrize(('password', 'exception'),
                             [('', EmptyPasswordError),
                             ('1234', ShortPasswordError),
                             ('123456789', PasswordConfirmMismatchError)
                              ])
    def test_raises_errors(self, request, password, exception):
        with pytest.raises(exception):
            validate_passsword(request, password)

    @pytest.mark.parametrize('length', [5, 6])
    def test_password_generator(self, length):
        assert len(password_generator(length)) == length

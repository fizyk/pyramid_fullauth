import pytest
from mock import Mock
from pyramid_fullauth.tools import validate_passsword
from pyramid_fullauth.exceptions import (
    EmptyPasswordError, ShortPasswordError, PasswordConfirmMismatchError
)


@pytest.fixture()
def request():
    request = Mock()

    def _(message, *args, **kwargs):
        return message
    request._ = Mock(side_effect=_)
    request.configure_mock(
        **{'config.fullauth.register.password':
            {'length_min': 8, 'confirm': True},
            'POST': {'confirm_password': '987654321'}
           }
    )

    return request


class TestTools(object):

    @pytest.mark.parametrize(('password', 'exception'),
                             [('', EmptyPasswordError),
                             ('1234', ShortPasswordError),
                             ('123456789', PasswordConfirmMismatchError)
                              ])
    def test_raises_errors(self, request, password, exception):
        with pytest.raises(exception):
            validate_passsword(request, password)

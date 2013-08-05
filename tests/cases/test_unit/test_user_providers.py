from pyramid.compat import text_type

from pyramid_fullauth.models import User
from pyramid_fullauth.models import AuthenticationProvider


def test_user_provider_id(db_with_user):

    user = db_with_user.query(User).filter(User.email == text_type('email@example.com')).one()
    # Provider does not exists yet
    assert not user.provider_id('email')

    provider = AuthenticationProvider()
    provider.provider = text_type('email')
    provider.provider_id = user.email
    user.providers.append(provider)
    db_with_user.commit()

    user = db_with_user.query(User).filter(User.email == text_type('email@example.com')).one()
    # Provider does not exists yet
    assert user.provider_id('email')

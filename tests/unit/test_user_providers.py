from pyramid.compat import text_type
import transaction

from pyramid_fullauth.models import User
from pyramid_fullauth.models import AuthenticationProvider


def test_user_provider_id(db_session, user):

    user = db_session.merge(user)
    # Provider does not exists yet
    assert not user.provider_id('email')

    provider = AuthenticationProvider()
    provider.provider = text_type('email')
    provider.provider_id = user.email
    user.providers.append(provider)
    transaction.commit()

    user = db_session.query(User).filter(User.email == text_type('email@example.com')).one()
    # Provider exists
    assert user.provider_id('email')
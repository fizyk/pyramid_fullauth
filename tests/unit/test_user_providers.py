"""Test provider related user methods."""
from pyramid.compat import text_type
import transaction

from pyramid_fullauth.models import User
from pyramid_fullauth.models import AuthenticationProvider


def test_user_provider_id(db_session, user):
    """User provider_id returns proper provider identification."""
    user = db_session.merge(user)
    email = user.email
    # Provider does not exists yet
    assert not user.provider_id('email')

    provider = AuthenticationProvider()
    provider.provider = text_type('email')
    provider.provider_id = email
    user.providers.append(provider)
    transaction.commit()

    user = db_session.query(User).filter(User.email == email).one()
    # Provider exists
    assert user.provider_id('email') == email

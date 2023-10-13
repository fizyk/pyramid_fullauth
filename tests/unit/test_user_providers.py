"""Test provider related user methods."""
import transaction

from pyramid_fullauth.models import AuthenticationProvider, User


def test_user_provider_id(db_session, user):
    """User provider_id returns proper provider identification."""
    user = db_session.merge(user)
    email = user.email
    # Provider does not exists yet
    assert not user.provider_id("email")

    provider = AuthenticationProvider()
    provider.provider = "email"
    provider.provider_id = email
    user.providers.append(provider)
    transaction.commit()

    user = db_session.query(User).filter(User.email == email).one()
    # Provider exists
    assert user.provider_id("email") == email

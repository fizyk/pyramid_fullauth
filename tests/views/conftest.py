"""General view fixtures."""
import pytest
import transaction

from pyramid_fullauth.models import AuthenticationProvider


@pytest.fixture
def facebook_user(active_user, db_session):
    """Facebook user."""
    active_user = db_session.merge(active_user)
    active_user.providers.append(
        AuthenticationProvider(provider='facebook', provider_id='1234'))
    transaction.commit()
    return db_session.merge(active_user)

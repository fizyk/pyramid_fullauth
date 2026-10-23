"""Test groupfinder."""

import pytest
import transaction

from pyramid_fullauth.auth import groupfinder


@pytest.mark.parametrize(
    ["is_admin", "is_active", "groups"],
    [
        (True, True, ["s:superadmin", "s:user"]),
        (True, False, ["s:superadmin", "s:inactive"]),
        (False, True, ["s:user"]),
        (False, False, ["s:inactive"]),
    ],
)
def test_groupfinder(web_request, db_session, user, is_admin, is_active, groups):
    """Return special group assigned for user."""
    user = db_session.merge(user)
    user.is_admin = is_admin
    user.is_active = is_active

    web_request.user = user
    assigned_groups = groupfinder(user.id, web_request)
    assert groups == assigned_groups


def test_groupfinder_detached_user(web_request, db_session, active_user):
    """Return groups even if request.user got detached by the transaction commit."""
    user = db_session.merge(active_user)
    user_id = user.id
    web_request.user = user
    transaction.commit()

    assert groupfinder(user_id, web_request) == ["s:user"]

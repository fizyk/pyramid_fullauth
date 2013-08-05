import pytest

from pyramid_fullauth.auth import groupfinder
from pyramid_fullauth.models import User


@pytest.mark.parametrize(['is_admin', 'is_active', 'groups'],
                         [(True, True, ['s:superadmin', 's:user']),
                         (True, False, ['s:superadmin', 's:inactive']),
                         (False, True, ['s:user']),
                         (False, False, ['s:inactive'])])
def test_groupfinder(web_request, db_with_user, is_admin, is_active, groups):
    user = db_with_user.query(User).all()[0]
    user.is_admin = is_admin
    user.is_active = is_active

    web_request.user = user
    assigned_groups = groupfinder(user.id, web_request)
    assert groups == assigned_groups

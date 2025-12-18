"""Unittest for social login view."""

import mock
import pytest
from velruse import AuthenticationComplete

from pyramid_fullauth.views.social import SocialLoginViews


@pytest.mark.parametrize(
    "profile, email",
    [
        (
            {
                "accounts": [{"domain": "facebook.com", "userid": "2343"}],
                "displayName": "teddy",
                "verifiedEmail": "verified@email.co.uk",
                "preferredUsername": "teddy",
                "emails": [{"value": "aasd@bwwqwe.pl"}],
                "name": "ted",
            },
            "verified@email.co.uk",
        ),
        (
            {
                "accounts": [{"domain": "facebook.com", "userid": "2343"}],
                "displayName": "teddy",
                "preferredUsername": "teddy",
                "emails": [{"value": "aasd@bwwqwe.pl"}],
                "name": "ted",
            },
            "aasd@bwwqwe.pl",
        ),
        (
            {
                "accounts": [{"domain": "facebook.com", "userid": "2343"}],
                "displayName": "teddy",
                "preferredUsername": "teddy",
                "emails": [{}],
                "name": "ted",
            },
            "2343@facebook.com",
        ),
        (
            {
                "accounts": [{"domain": "facebook.com", "userid": "2343"}],
                "displayName": "teddy",
                "preferredUsername": "teddy",
                "emails": [],
                "name": "ted",
            },
            "2343@facebook.com",
        ),
        (
            {
                "accounts": [{"domain": "facebook.com", "userid": "2343"}],
                "displayName": "teddy",
                "preferredUsername": "teddy",
                "name": "ted",
            },
            "2343@facebook.com",
        ),
    ],
)
def test_email_from_context(profile, email):
    """Test email_from_context email getting method."""
    context = AuthenticationComplete(
        profile,
        {"oauthAccessToken": "7897048593434"},
        "facebook",
        "facebook",
    )
    view = SocialLoginViews(mock.MagicMock())
    assert view._email_from_context(context) == email

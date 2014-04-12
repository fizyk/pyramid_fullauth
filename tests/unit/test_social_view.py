"""Unittest for social login view."""
import pytest
import mock
from velruse import AuthenticationComplete

from pyramid_fullauth.views.social import SocialLoginViews


@pytest.mark.parametrize('profile, email', [
    (
        {
            'accounts': [{'domain': u'facebook.com', 'userid': u'2343'}],
            'displayName': u'teddy',
            'verifiedEmail': 'verified@email.co.uk',
            'preferredUsername': u'teddy',
            'emails': [{'value': u'aasd@bwwqwe.pl'}],
            'name': u'ted'
        },
        'verified@email.co.uk'
    ), (
        {
            'accounts': [{'domain': u'facebook.com', 'userid': u'2343'}],
            'displayName': u'teddy',
            'preferredUsername': u'teddy',
            'emails': [{'value': u'aasd@bwwqwe.pl'}],
            'name': u'ted'
        },
        'aasd@bwwqwe.pl'
    ), (
        {
            'accounts': [{'domain': u'facebook.com', 'userid': u'2343'}],
            'displayName': u'teddy',
            'preferredUsername': u'teddy',
            'emails': [{}],
            'name': u'ted'
        },
        '2343@facebook.com'
    ), (
        {
            'accounts': [{'domain': u'facebook.com', 'userid': u'2343'}],
            'displayName': u'teddy',
            'preferredUsername': u'teddy',
            'emails': [],
            'name': u'ted'
        },
        '2343@facebook.com'
    ), (
        {
            'accounts': [{'domain': u'facebook.com', 'userid': u'2343'}],
            'displayName': u'teddy',
            'preferredUsername': u'teddy',
            'name': u'ted'
        },
        '2343@facebook.com'
    ),
])
def test_email_from_context(profile, email):
    """Test email_from_context email getting method."""
    context = AuthenticationComplete(
        profile,
        {'oauthAccessToken': '7897048593434'},
        u'facebook',
        u'facebook')
    view = SocialLoginViews(mock.MagicMock())
    assert view._email_from_context(context) == email

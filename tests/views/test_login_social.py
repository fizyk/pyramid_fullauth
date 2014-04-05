"""Social network login test."""
import transaction
from pyramid import testing
from velruse import AuthenticationComplete
from mock import MagicMock

from pyramid_fullauth.views.social import SocialLoginViews
from pyramid_fullauth.models import User


def test_social_login_link(social_app):
    """Login:Form displayed social form."""
    res = social_app.get('/login')
    assert ('Connect with facebook</a>' in res.body)


def test_social_click_link(social_app):
    """Click social login link."""
    res = social_app.get('/login/facebook?scope=email%2Coffline_access', status=302)
    assert (res.headers['Location'].startswith(
        'https://www.facebook.com/dialog/oauth/?scope=email%2Coffline_access&state='))


def test_social_login_register(social_config, db_session):
    """Register fresh user and logs him in."""
    profile = {
        'accounts': [{'domain': u'facebook.com', 'userid': u'2343'}],
        'displayName': u'teddy',
        'verifiedEmail': u'we@po.pl',
        'preferredUsername': u'teddy',
        'emails': [{'value': u'aasd@bwwqwe.pl'}],
        'name': u'ted'
    }
    credentials = {'oauthAccessToken': '7897048593434'}
    provider_name = u'facebook'
    provider_type = u'facebook'
    request = testing.DummyRequest()
    request.user = None
    request.registry = social_config.registry
    request.remote_addr = u'127.0.0.123'
    request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)

    request.login_perform = MagicMock(name='login_perform')
    request.login_perform.return_value = {'status': True}
    view = SocialLoginViews(request)
    out = view()
    assert out == {'status': True}
    transaction.commit()

    # read first new account
    user = db_session.query(User).one()
    assert user.is_active
    assert user.provider_id('facebook') == profile['accounts'][0]['userid']


def test_login_social_connect(social_config, active_user, db_session):
    """Connect and logs user in."""
    user = db_session.merge(active_user)

    profile = {
        'accounts': [{'domain': u'facebook.com', 'userid': u'2343'}],
        'displayName': u'teddy',
        'preferredUsername': u'teddy',
        'emails': [{'value': user.email}],
        'name': u'ted'
    }
    credentials = {'oauthAccessToken': '7897048593434'}
    provider_name = u'facebook'
    provider_type = u'facebook'
    user = None
    request = testing.DummyRequest()
    request.user = user
    request.registry = social_config.registry
    request.remote_addr = u'127.0.0.123'
    request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)

    request.login_perform = MagicMock(name='login_perform')
    request.login_perform.return_value = {'status': True}
    view = SocialLoginViews(request)
    out = view()
    assert out == {'status': True}

    user = db_session.merge(active_user)
    assert user.provider_id('facebook') == profile['accounts'][0]['userid']


def test_logged_social_connect_account(social_config, active_user, db_session):
    """Connect facebook account to logged in user."""
    user = db_session.merge(active_user)

    profile = {
        'accounts': [{'domain': u'facebook.com', 'userid': u'2343'}],
        'displayName': u'teddy',
        'preferredUsername': u'teddy',
        'emails': [{'value': u'aasd@basd.pl'}],
        'name': u'ted'
    }
    credentials = {'oauthAccessToken': '7897048593434'}
    provider_name = u'facebook'
    provider_type = u'facebook'
    request = testing.DummyRequest()
    request.user = user
    request.registry = social_config.registry
    request.remote_addr = u'127.0.0.123'
    request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)

    request.login_perform = MagicMock(name='login_perform')
    request.login_perform.return_value = {'status': True}
    view = SocialLoginViews(request)
    out = view()
    assert out == {'status': True}

    transaction.commit()
    user = db_session.merge(user)
    assert user.provider_id('facebook') == profile['accounts'][0]['userid']

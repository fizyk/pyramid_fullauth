# -*- coding: utf-8 -*-

from tests.utils import BaseTestSuite


class TestSocialLogin(BaseTestSuite):

    def test_social_login(self, base_app):
        '''Login:Form displayed social form'''
        res = base_app.app.get('/login')
        assert ('Connect with facebook</a>' in res.body)

    def test_click_link(self, base_app):
        '''Login:Social form'''
        res = base_app.app.get('/login/facebook?scope=email%2Coffline_access', status=302)
        assert (res.headers['Location'].startswith(
            'https://www.facebook.com/dialog/oauth/?scope=email%2Coffline_access&state='))

    # does it test anything?
    def _test_login_no_user_no_verified_no_email(self, base_app):
        '''Login:Social form'''
        from pyramid_fullauth.views.social import SocialLoginViews
        from pyramid import testing
        from velruse import AuthenticationComplete
        from mock import MagicMock

        profile = {
            'accounts': [{'domain': u'facebook.com', 'userid': u'2343'}],
            'displayName': u'teddy',
            'preferredUsername': u'teddy',
            'emails': [{'value': u'aewrew@bzxczxc.pl'}],
            'name': u'ted'
        }
        credentials = {'oauthAccessToken': '7897048593434'}
        provider_name = u'facebook'
        provider_type = u'facebook'
        user = None
        request = testing.DummyRequest()
        request.user = user
        request.config = base_app.config.registry['config']
        request.remote_addr = u'127.0.0.123'
        request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)

        request.login_perform = MagicMock(name='login_perform')
        request.login_perform.return_value = {'status': True}
        sv = SocialLoginViews(request)
        out = sv.register_social()
        assert out == {'status': True}

    def test_login_no_user_email_verifed(self, base_app):
        '''Login:Social form'''
        from pyramid_fullauth.views.social import SocialLoginViews
        from pyramid import testing
        from velruse import AuthenticationComplete
        from mock import MagicMock

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
        user = None
        request = testing.DummyRequest()
        request.user = user
        request.registry = base_app.config.registry
        request.remote_addr = u'127.0.0.123'
        request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)

        request.login_perform = MagicMock(name='login_perform')
        request.login_perform.return_value = {'status': True}
        sv = SocialLoginViews(request)
        out = sv.register_social()
        assert out == {'status': True}

    def test_login_success(self, base_app):
        '''Login:Social form'''
        from pyramid_fullauth.views.social import SocialLoginViews
        from pyramid import testing
        from velruse import AuthenticationComplete
        from mock import MagicMock

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
        user = self.read_user(self.user_data['email'])
        request = testing.DummyRequest()
        request.user = user
        request.registry = base_app.config.registry
        request.remote_addr = u'127.0.0.123'
        request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)

        request.login_perform = MagicMock(name='login_perform')
        request.login_perform.return_value = {'status': True}
        sv = SocialLoginViews(request)
        out = sv.register_social()
        assert out == {'status': True}

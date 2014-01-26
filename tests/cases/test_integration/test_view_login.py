# -*- coding: utf-8 -*-

import time
from tests.utils import BaseTestSuite


class TestLogin(BaseTestSuite):

    def check_if_logged(self, app):
        '''
        Checks for auth_tkt cookies beeing set
        '''
        cookies = app.cookies
        if 'auth_tkt' in cookies and cookies['auth_tkt']:

            return True
        return False

    def test_login_view(self, base_app):
        '''Login:Form displayed'''

        res = base_app.app.get('/login')
        assert '<form id="login_form"' in res.body

    def test_login_view_secret(self, base_app):
        '''Login:Form displayed after redirect'''
        res = base_app.app.get('/secret', status=302)
        # check if redirect is correct
        assert res.headers['Location'] == 'http://localhost/login?after=%2Fsecret'
        # redirecting
        res = base_app.app.get(res.headers['Location'])
        assert '<form id="login_form"' in res.body

    def test_login(self, base_app):
        '''Login:Action test with clicks'''
        self.create_user({'is_active': True})

        res = base_app.app.get('/secret', status=302)
        assert res
        res = base_app.app.get('/login?after=%2Fsecret')

        assert self.check_if_logged(base_app.app) == False

        res.form.set('email', self.user_data['email'])
        res.form.set('password', self.user_data['password'])
        res = res.form.submit()

        assert self.check_if_logged(base_app.app) == True
        assert res.status == '302 Found'
        assert not 'Max-Age=' in str(res)

    def test_login_remember(self, base_app):
        '''Login:Action test with clicks'''
        self.create_user({'is_active': True})

        res = base_app.app.get('/login')
        assert self.check_if_logged(base_app.app) == False

        res.form.set('email', self.user_data['email'])
        res.form.set('password', self.user_data['password'])
        res.form.set('remember', '1')
        res = res.form.submit()

        assert self.check_if_logged(base_app.app) == True
        assert 'Max-Age=' in str(res)

    def test_login_inactive(self, base_app):
        '''Login:Action test with clicks if user is inactive'''
        self.create_user()
        res = base_app.app.get('/login')

        assert self.check_if_logged(base_app.app) == False

        res.form.set('email', self.user_data['email'])
        res.form.set('password', self.user_data['password'])
        res = res.form.submit()

        assert self.check_if_logged(base_app.app) == True
        assert res.status == '302 Found'

    def test_login_post(self, base_app):
        '''Login:Action test send post simply'''
        self.create_user({'is_active': True})

        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'csrf_token': self.get_token('/login?after=%2Fsecret', base_app.app)
        }
        res = base_app.app.get('/secret', status=302)
        assert res
        res = base_app.app.post('/login?after=%2Fsecret', post_data)

        assert self.check_if_logged(base_app.app) == True
        assert res.status == '302 Found'

    def test_login_wrong(self, base_app):
        '''Login:Action test: wrong password'''
        self.create_user({'is_active': True})

        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'] + u'asasa',
            'csrf_token': self.get_token('/login', base_app.app)
        }
        res = base_app.app.get('/login', status=200)
        assert res
        res = base_app.app.post('/login', post_data)

        assert '<div class="alert alert-error">Error! Wrong e-mail or password.</div>' in res
        assert res

    def test_login_no_csrf(self, base_app):
        '''Login:Action test: no csrf token'''
        self.create_user({'is_active': True})

        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
        }
        res = base_app.app.get('/login', status=200)
        assert res
        res = base_app.app.post('/login', post_data, status=401)

        assert self.check_if_logged(base_app.app) == False

    def test_login_wrong_csrf(self, base_app):
        '''Login:Action test: wrong password'''
        self.create_user({'is_active': True})

        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'csrf_token': '8934798289723789347892397832789432789'
        }
        res = base_app.app.get('/login', status=200)
        assert res
        res = base_app.app.post('/login', post_data, status=401)
        assert self.check_if_logged(base_app.app) == False

    def test_logout(self, base_app):
        '''Logout:Action test'''
        self.create_user({'is_active': True})

        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'csrf_token': self.get_token('/login', base_app.app)
        }
        res = base_app.app.post('/login', post_data, status=302)
        assert self.check_if_logged(base_app.app) == True

        res = base_app.app.get('/logout', status=302)
        assert res
        assert self.check_if_logged(base_app.app) == False
        res = base_app.app.get('/secret', status=302)
        assert res

    def test_automatic_logout(self, base_app):
        ''' Test user logged out after
            defined period of inactivity
        '''

        timeout = base_app.config.registry['config']['fullauth']['AuthTkt']['timeout'] + 1

        self.create_user({'is_active': True})
        self.authenticate(base_app.app)
        # Simulating inactivity
        time.sleep(timeout)
        res = base_app.app.get('/email/change')
        assert res.headers['Location'] == 'http://localhost/login?after=%2Femail%2Fchange'
        res = base_app.app.get(res.headers['Location'])
        assert '<form id="login_form"' in res.body

    def test_automatic_logout_not_expired(self, base_app):
        ''' Test user not logged out,
            timeout did not expire
        '''
        timeout = base_app.config.registry['config']['fullauth']['AuthTkt']['timeout'] - 1

        self.create_user({'is_active': True})
        self.authenticate(base_app.app)
        # Simulating inactivity
        time.sleep(timeout)
        res = base_app.app.get('/email/change')
        assert '<input type="email" placeholder="username@hostname.com" name="email" id="change[email]"/>' in res.body

    def test_login_success_xhr(self, base_app):
        self.create_user({'is_active': True})

        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'csrf_token': self.get_token('/login?after=%2Fsecret', base_app.app)
        }
        res = base_app.app.get('/secret', status=302)
        assert res
        postRes = base_app.app.post('/login?after=%2Fsecret',
                                    post_data,
                                    headers={
                                    'X-Requested-With': 'XMLHttpRequest'},
                                    expect_errors=True)
        assert postRes.content_type == 'application/json'
        assert self.check_if_logged(base_app.app) == True
        assert postRes.json['status']

    def test_default_login_noredirect(self, app_authable):
        self.create_user({'is_active': True})
        authres = self.authenticate(app_authable.app)
        res = authres.goto('/secret', status=403)
        assert res
        res = authres.goto('/login')
        assert res
        assert '<form id="login_form"' in res.body
        res = authres.goto('/secret', status=403)
        assert res


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

# -*- coding: utf-8 -*-

import time
from tests import BaseTestCase


class LoginTest(BaseTestCase):

    def test_login_view(self):
        '''Login:Form displayed'''
        res = self.app.get('/login')
        self.assertTrue('<form id="login_form"' in res.body)

    def test_login_view_secret(self):
        '''Login:Form displayed after redirect'''
        res = self.app.get('/secret', status=302)
        # check if redirect is correct
        self.assertTrue(res.headers['Location'] == 'http://localhost/login?after=%2Fsecret')
        # redirecting
        res = self.app.get(res.headers['Location'])
        self.assertTrue('<form id="login_form"' in res.body)

    def test_login(self):
        '''Login:Action test with clicks'''
        self.create_user({'is_active': True})

        res = self.app.get('/secret', status=302)
        assert res
        res = self.app.get('/login?after=%2Fsecret')
        if self.config.registry['config'].fullauth.session_factory.default == 'unencrypted':
            self.assertTrue(len(res.headers['Set-Cookie']) > 150)

        res.form.set('email', self.user_data['email'])
        res.form.set('password', self.user_data['password'])
        res = res.form.submit()

        self.assertTrue(len(res.headers['Set-Cookie']) > 150)
        self.assertEqual(res.status, '302 Found')
        self.assertFalse('Max-Age=' in str(res))

    def test_login_remember(self):
        '''Login:Action test with clicks'''
        self.create_user({'is_active': True})

        res = self.app.get('/secret', status=302)
        assert res
        res = self.app.get('/login?after=%2Fsecret')
        if self.config.registry['config'].fullauth.session_factory.default == 'unencrypted':
            self.assertTrue(len(res.headers['Set-Cookie']) > 150)

        res.form.set('email', self.user_data['email'])
        res.form.set('password', self.user_data['password'])
        res.form.set('remember', '1')
        res = res.form.submit()

        self.assertTrue(len(res.headers['Set-Cookie']) > 150)
        self.assertEqual(res.status, '302 Found')
        self.assertTrue('Max-Age=' in str(res))

    def test_login_inactive(self):
        '''Login:Action test with clicks if user is inactive'''
        self.create_user()
        res = self.app.get('/login')
        if self.config.registry['config'].fullauth.session_factory.default == 'unencrypted':
            self.assertTrue(len(res.headers['Set-Cookie']) > 150)

        res.form.set('email', self.user_data['email'])
        res.form.set('password', self.user_data['password'])
        res = res.form.submit()

        self.assertTrue(len(res.headers['Set-Cookie']) > 150)
        self.assertEqual(res.status, '302 Found')

    def test_login_post(self):
        '''Login:Action test send post simply'''
        self.create_user({'is_active': True})

        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'token': self.get_token('/login?after=%2Fsecret')
        }
        res = self.app.get('/secret', status=302)
        assert res
        res = self.app.post('/login?after=%2Fsecret', post_data)
        self.assertTrue(len(res.headers['Set-Cookie']) > 150)
        self.assertEqual(res.status, '302 Found')

    def test_login_wrong(self):
        '''Login:Action test: wrong password'''
        self.create_user({'is_active': True})

        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'] + u'asasa',
            'token': self.get_token('/login')
        }
        res = self.app.get('/login', status=200)
        assert res
        res = self.app.post('/login', post_data)
        self.assertTrue('<div class="alert alert-error">Error! Wrong e-mail or password.</div>' in res)
        assert res

    def test_login_no_csrf(self):
        '''Login:Action test: wrong password'''
        self.create_user({'is_active': True})

        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
        }
        res = self.app.get('/login', status=200)
        assert res
        res = self.app.post('/login', post_data)
        self.assertTrue('<div class="alert alert-error">Error! CSRF token did not match.</div>' in res)
        assert res

    def test_login_wrong_csrf(self):
        '''Login:Action test: wrong password'''
        self.create_user({'is_active': True})

        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'token': '8934798289723789347892397832789432789'
        }
        res = self.app.get('/login', status=200)
        assert res
        res = self.app.post('/login', post_data)
        self.assertTrue('<div class="alert alert-error">Error! CSRF token did not match.</div>' in res)
        assert res

    def test_logout(self):
        '''Logout:Action test'''
        self.create_user({'is_active': True})

        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'token': self.get_token('/login')
        }
        res = self.app.post('/login', post_data, status=302)
        self.assertTrue(len(res.headers['Set-Cookie']) > 150)

        res = self.app.get('/logout', status=302)
        assert res
        self.assertTrue(len(res.headers['Set-Cookie']) < 100)
        res = self.app.get('/secret', status=302)
        assert res

    def test_automatic_logout(self):
        ''' Test user logged out after
            defined period of inactivity
        '''
        try:
            timeout = self.config.registry['config']['fullauth']['AuthTkt']['timeout'] + 1
        except KeyError:
        # Timeout can be optional in settings
            return
        self.create_user({'is_active': True})
        self.authenticate()
        # Simulating inactivity
        time.sleep(timeout)
        res = self.app.get('/email/change')
        self.assertTrue(res.headers['Location'] == 'http://localhost/login?after=%2Femail%2Fchange')
        res = self.app.get(res.headers['Location'])
        self.assertTrue('<form id="login_form"' in res.body)

    def test_automatic_logout_not_expired(self):
        ''' Test user not logged out,
            timeout did not expire
        '''
        try:
            timeout = self.config.registry['config']['fullauth']['AuthTkt']['timeout'] - 1
        except KeyError:
        # Timeout can be optional in settings
            return
        self.create_user({'is_active': True})
        self.authenticate()
        # Simulating inactivity
        time.sleep(timeout)
        res = self.app.get('/email/change')
        self.assertTrue(
            '<input type="email" placeholder="username@hostname.com" name="email" id="change[email]"/>' in res.body)

    def test_login_xhr_response(self):
        '''Login:Xhr repsonse'''
        res = self.app.post('/login', '', headers={'X-Requested-With': 'XMLHttpRequest'}, expect_errors=True)
        self.assertTrue(res.content_type == 'application/json')
        self.failUnless(u'status' in res.json)
        self.assertTrue(not res.json['status'])

    def test_login_success_xhr(self):
        self.create_user({'is_active': True})

        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'token': self.get_token('/login?after=%2Fsecret')
        }
        res = self.app.get('/secret', status=302)
        assert res
        postRes = self.app.post('/login?after=%2Fsecret', post_data, headers={
                                'X-Requested-With': 'XMLHttpRequest'}, expect_errors=True)
        self.assertTrue(postRes.content_type == 'application/json')
        self.assertTrue(len(postRes.headers['Set-Cookie']) > 150)
        self.assertTrue(postRes.json['status'])


class SocialLoginTest(BaseTestCase):

    def test_social_login(self):
        '''Login:Form displayed social form'''
        res = self.app.get('/login')
        self.assertTrue('Connect with facebook</a>' in res.body)

    def test_click_link(self):
        '''Login:Social form'''
        res = self.app.get('/login/facebook?scope=email%2Coffline_access', status=302)
        self.assertTrue(res.headers['Location'].startswith(
            'https://www.facebook.com/dialog/oauth/?scope=email%2Coffline_access&state='))

    def test_login_no_user(self):
        '''Login:Social form'''
        from pyramid import testing
        from velruse import AuthenticationComplete
        from mock import MagicMock

        profile = {
            'accounts': [{'domain': u'facebook.com', 'userid': u'2343'}],
            'displayName': u'teddy',
            'gender': None,
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
        request.config = self.config
        request.remote_addr = u'127.0.0.12'
        request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)

        request.login_perform = MagicMock(name='login_perform')
        request.login_perform.return_value = {'status': True}

    def test_login_no_user_no_verified_no_email(self):
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
        request.config = self.config.registry['config']
        request.remote_addr = u'127.0.0.123'
        request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)

        request.login_perform = MagicMock(name='login_perform')
        request.login_perform.return_value = {'status': True}
        sv = SocialLoginViews(request)
        out = sv.register_social()
        self.assertEqual(out, {'status': True})

    def test_login_no_user_email_verifed(self):
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
        request.config = self.config.registry['config']
        request.remote_addr = u'127.0.0.123'
        request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)

        request.login_perform = MagicMock(name='login_perform')
        request.login_perform.return_value = {'status': True}
        sv = SocialLoginViews(request)
        out = sv.register_social()
        self.assertEqual(out, {'status': True})

    def test_login_success(self):
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
        request.config = self.config.registry['config']
        request.remote_addr = u'127.0.0.123'
        request.context = AuthenticationComplete(profile, credentials, provider_name, provider_type)

        request.login_perform = MagicMock(name='login_perform')
        request.login_perform.return_value = {'status': True}
        sv = SocialLoginViews(request)
        out = sv.register_social()
        self.assertEqual(out, {'status': True})

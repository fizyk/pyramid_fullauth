# -*- coding: utf-8 -*-

import warnings
from HTMLParser import HTMLParser
from tests.utils import BaseTestSuite


class TestRegister(BaseTestSuite):

    def test_register_view(self, base_app):
        '''Register:Form displayed'''
        res = base_app.app.get('/register')
        assert '<form class="registerForm"' in res.body

    def test_register_action(self, base_app):
        '''
            Register:Register user
        '''
        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'],
            'csrf_token': self.get_token('/register', base_app.app)
        }
        user = self.read_user(self.user_data['email'])
        assert user is None

        res = base_app.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        assert res
        user = self.read_user(self.user_data['email'])

        assert not user is None
        assert not user.is_active == 'User should not have active account at this moment'

    def test_register_second_time_action(self, base_app):
        '''
            Register:Register user Second try
        '''
        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'],
            'csrf_token': self.get_token('/register', base_app.app)
        }
        user = self.read_user(self.user_data['email'])
        assert user is None

        res = base_app.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        assert res
        user = self.read_user(self.user_data['email'])
        assert user is not None
        # second try
        res = base_app.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        assert res
        assert user is not None
        assert 'User with given e-mail already exists' in res.body
        # User should not have active account at this moment
        assert not user.is_active

    def test_register_not_unicode_form_action(self, base_app):
        '''
            Register:Register user without Unicode data
        '''
        post_data = {
            'email': str(self.user_data['email']),
            'password': str(self.user_data['password']),
            'confirm_password': str(self.user_data['password']),
            'csrf_token': self.get_token('/register', base_app.app)
        }
        user = self.read_user(self.user_data['email'])
        assert user is None
        res = base_app.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        assert res
        user = self.read_user(self.user_data['email'])
        assert user is not None

    def test_register_not_full_form_action(self, base_app):
        '''
            Register:Register user without full form
        '''
        post_data = {
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'],
            'csrf_token': self.get_token('/register', base_app.app)
        }
        user = self.read_user(self.user_data['email'])
        assert user is None
        with warnings.catch_warnings(True) as w:
            res = base_app.app.post('/register', post_data,
                                    extra_environ={'REMOTE_ADDR': '0.0.0.0'})
            assert res
            # Not full filled POST should not raise a Warning!
            assert len(w) == 0
        user = self.read_user(self.user_data['email'])
        assert (user is None)

    def test_register_action_wrong_password(self, base_app):
        '''
            Register:Register user: Wrong passwords
        '''
        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'] + u'sasasasa',
            'csrf_token': self.get_token('/register', base_app.app)
        }
        user = self.read_user(self.user_data['email'])
        assert user is None
        res = base_app.app.post('/register', post_data,
                                extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        assert '<div class="control-group error">' in res
        assert 'Passwords don\'t match' in HTMLParser().unescape(res.body)
        user = self.read_user(self.user_data['email'])
         # User profile should not be created!
        assert user is None

    def test_register_action_wrong_csrf(self, base_app):
        '''
            Register:Register user: Wrong csrf
        '''
        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'] + u'sasasasa',
            'csrf_token': self.get_token('/register', base_app.app) + '1'
        }
        user = self.read_user(self.user_data['email'])
        assert user is None
        res = base_app.app.post('/register', post_data,
                                extra_environ={'REMOTE_ADDR': '0.0.0.0'},
                                status=401)

        user = self.read_user(self.user_data['email'])
        # User profile should not be created!
        assert user is None

    def test_register_action_very_long_email(self, base_app):
        '''
            Register:Register user: Wrong email - too long
        '''
        email = u'email' * 100 + '@wap.pl'
        post_data = {
            'email': email,
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'],
            'csrf_token': self.get_token('/register', base_app.app)
        }
        user = self.read_user(email)
        assert user is None

        res = base_app.app.post('/register', post_data,
                                extra_environ={'REMOTE_ADDR': '0.0.0.0'})

        assert '<div class="control-group error">' in res
        assert 'Incorrect e-mail format' in res
        user = self.read_user(email)
         # User with too long email should not be created
        assert user is None

    def test_register_action_empty_email(self, base_app):
        '''
            Register:Register user: Wrong email - empty
        '''
        post_data = {
            'email': '',
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'],
            'csrf_token': self.get_token('/register', base_app.app)
        }

        res = base_app.app.post('/register', post_data,
                                extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        assert '<div class="control-group error">' in res
        assert 'E-mail is empty' in res

    def test_register_action_very_long_passwd(self, base_app):
        '''
            Register:Register user: Passwords - very long
        '''
        email = u'email@wap.pl'
        post_data = {
            'email': email,
            'password': self.user_data['password'] * 10000,
            'confirm_password': self.user_data['password'] * 10000,
            'csrf_token': self.get_token('/register', base_app.app)
        }
        user = self.read_user(email)
        assert user is None
        base_app.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        user = self.read_user(email)
        # User with very long password should be created
        assert user is not None
        # User should not have active account at this moment
        assert not user.is_active

    def test_register_action_short_passwd(self, base_app):
        '''
            Register:Register user: Password - too short
        '''
        email = u'email@wap.pl'
        post_data = {
            'email': email,
            'password': '12',
            'confirm_password': self.user_data['password'] * 10000,
            'csrf_token': self.get_token('/register', base_app.app)
        }
        user = self.read_user(email)
        assert user is None
        res = base_app.app.post('/register',
                                post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        user = self.read_user(email)
        # User with too short password should not be created
        assert user is None
        assert '<div class="control-group error">' in res
        assert 'Password is too short' in res.body

    def test_register_action_empty_passwd(self, base_app):
        '''
            Register:Register user: Empty password
        '''
        email = u'email@wap.pl'
        post_data = {
            'email': email,
            'password': '',
            'confirm_password': self.user_data['password'] * 10000,
            'csrf_token': self.get_token('/register', base_app.app)
        }
        user = self.read_user(email)
        assert user is None
        res = base_app.app.post('/register', post_data,
                                extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        user = self.read_user(email)
        # User with empty password should not be created
        assert user is None
        assert '<div class="control-group error">' in res
        assert 'Please enter your password' in res.body

    def test_account_activation(self, base_app):
        '''
            Register:Activate user
        '''
        self.create_user()
        user = self.read_user(self.user_data['email'])

        res = base_app.app.get('/register/activate/' + user.activate_key)
        assert res
        user = self.read_user(self.user_data['email'])

        assert not user.activate_key
        assert user.is_active
        assert user.activated_at

        # check if login works after activation
        res = base_app.app.get('/login')
        assert len(res.headers['Set-Cookie']) > 150
        res.form.set('email', self.user_data['email'])
        res.form.set('password', self.user_data['password'])
        res = res.form.submit()
        assert len(res.headers['Set-Cookie']) > 150
        assert res.status == '302 Found'

    def test_account_activation_wrong_key(self, base_app):
        '''
            Register:Activate user
        '''
        self.create_user()
        user = self.read_user(self.user_data['email'])
        activate_key = user.activate_key
        res = base_app.app.get('/register/activate/' + activate_key[:-5], status=200)
        assert res
        assert 'Invalid activation code' in res.body
        user = self.read_user(self.user_data['email'])
        assert user.activate_key == activate_key
        assert user.activate_key is not None
        assert not user.activated_at
        # User should not have active account at this moment
        assert not user.is_active

    def test_account_activation_key_with_trash_chars(self, base_app):
        '''
            Register:Activate user
        '''
        from urllib import quote
        self.create_user()
        user = self.read_user(self.user_data['email'])
        activate_key = user.activate_key
        res = base_app.app.get('/register/activate/' + quote(
            u'ąśðłĸęł¶→łęóħó³→←śðđ[]}³½ĸżćŋðń→↓ŧ¶ħ→ĸł¼²³↓←ħ@ĸđśðĸ@ł¼ęłśħđó[³²½łðśđħ'.encode('utf-8')), status=200)
        assert res
        assert 'Invalid activation code' in res.body
        user = self.read_user(self.user_data['email'])
        assert user.activate_key, activate_key
        assert not user.activate_key is None
        assert not user.activated_at
        # User should not have active account at this moment
        assert not user.is_active

    def test_account_activation_twice(self, base_app):
        '''
            Register:Activate user
        '''
        self.create_user()
        user = self.read_user(self.user_data['email'])
        activate_key = user.activate_key
        res = base_app.app.get('/register/activate/' + activate_key)
        assert res
        user = self.read_user(self.user_data['email'])
        assert not user.activate_key
        assert user.is_active
        assert user.activated_at

        # Try to access activate link again
        user = self.read_user(self.user_data['email'])
        res = base_app.app.get('/register/activate/' + activate_key, status=200)
        assert res
        assert 'Invalid activation code' in res.body

    def test_register_action_no_password_required(self,
                                                  app_no_password_required):
        '''
            Register:Register without password required
        '''
        post_data = {
            'email':
            self.user_data['email'],
            'csrf_token':
            self.get_token('/register', app_no_password_required.app)
        }
        user = self.read_user(self.user_data['email'])
        assert user is None

        res = app_no_password_required.app.post(
            '/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        assert res
        user = self.read_user(self.user_data['email'])

        assert user is not None
        # Emails should be the same
        assert user.email == post_data['email']

    def test_no_pass_confirm(self, app_no_password_confirm):
        '''
            Register: Register without password confirm option
        '''

        post_data = {
            'email':
            self.user_data['email'],
            'password':
            self.user_data['password'],
            'confirm_password':
            self.user_data['password'] + u'sasasasa',
            'csrf_token':
            self.get_token('/register', app_no_password_confirm.app)
        }

        user = self.read_user(self.user_data['email'])
        assert user is None
        res = app_no_password_confirm.app.post(
            '/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        assert not '<div class="control-group error">' in res
        assert not 'Passwords don\'t match!' in HTMLParser().unescape(res.body)
        user = self.read_user(self.user_data['email'])
        # User profile should be created!
        assert not user is None

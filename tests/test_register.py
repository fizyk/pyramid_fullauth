# -*- coding: utf-8 -*-

import warnings
from tests import BaseTestCase


class RegisterTest(BaseTestCase):

    def test_register_view(self):
        '''Register:Form displayed'''
        res = self.app.get('/register')
        self.failUnless('<form class="registerForm"' in res.body)

    def test_register_action(self):
        '''
            Register:Register user
        '''
        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'],
            'token': self.get_token('/register')
        }
        user = self.read_user(self.user_data['email'])
        self.assertTrue(user is None)

        res = self.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        assert res
        user = self.read_user(self.user_data['email'])

        self.assertFalse(user is None)
        self.assertFalse(user.is_active, 'User should not have active account at this moment')

    def test_register_second_time_action(self):
        '''
            Register:Register user Second try
        '''
        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'],
            'token': self.get_token('/register')
        }
        user = self.read_user(self.user_data['email'])
        self.assertTrue(user is None)

        res = self.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        assert res
        user = self.read_user(self.user_data['email'])
        self.assertTrue(user is not None)
        # second try
        res = self.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        assert res
        self.assertTrue(user is not None)
        self.failUnless(
            'User with given e-mail already exists' in self.htmlToText(res.body))
        self.assertFalse(user.is_active, 'User should not have active account at this moment')

    def test_register_not_unicode_form_action(self):
        '''
            Register:Register user without Unicode data
        '''
        post_data = {
            'email': str(self.user_data['email']),
            'password': str(self.user_data['password']),
            'confirm_password': str(self.user_data['password']),
            'token': self.get_token('/register')
        }
        user = self.read_user(self.user_data['email'])
        self.assertTrue(user is None)
        res = self.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        assert res
        user = self.read_user(self.user_data['email'])
        self.assertTrue(user is not None)

    def test_register_not_full_form_action(self):
        '''
            Register:Register user without full form
        '''
        post_data = {
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'],
            'token': self.get_token('/register')
        }
        user = self.read_user(self.user_data['email'])
        self.assertTrue(user is None)
        with warnings.catch_warnings(True) as w:
            res = self.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
            assert res
            self.assertEqual(len(w), 0, 'Not full filled POST should not raise a Warning!')
        user = self.read_user(self.user_data['email'])
        self.assertTrue(user is None)

    def test_register_action_wrong_password(self):
        '''
            Register:Register user: Wrong passwords
        '''
        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'] + u'sasasasa',
            'token': self.get_token('/register')
        }
        user = self.read_user(self.user_data['email'])
        self.assertTrue(user is None)
        res = self.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        self.failUnless('<div class="control-group error">' in res)
        self.failUnless('Passwords don\'t match' in self.htmlToText(res.body))
        user = self.read_user(self.user_data['email'])
        self.assertTrue(user is None, 'User profile should not be created!')

    def test_register_action_wrong_csrf(self):
        '''
            Register:Register user: Wrong csrf
        '''
        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'] + u'sasasasa',
            'token': self.get_token('/register') + '1'
        }
        user = self.read_user(self.user_data['email'])
        self.assertTrue(user is None)
        res = self.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})

        self.failUnless('CSRF token did not match.' in self.htmlToText(res.body))
        user = self.read_user(self.user_data['email'])
        self.assertTrue(user is None, 'User profile should not be created!')

    def test_register_action_very_long_email(self):
        '''
            Register:Register user: Wrong email - too long
        '''
        email = u'email' * 100 + '@wap.pl'
        post_data = {
            'email': email,
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'],
            'token': self.get_token('/register')
        }
        user = self.read_user(email)
        self.assertTrue(user is None)

        res = self.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})

        self.failUnless('<div class="control-group error">' in res)
        self.failUnless('Incorrect e-mail format' in res)
        user = self.read_user(email)
        self.assertTrue(user is None, 'User with too long email should not be created')

    def test_register_action_empty_email(self):
        '''
            Register:Register user: Wrong email - empty
        '''
        post_data = {
            'email': '',
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'],
            'token': self.get_token('/register')
        }

        res = self.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        self.failUnless('<div class="control-group error">' in res)
        self.failUnless('E-mail is empty' in res)

    def test_register_action_very_long_passwd(self):
        '''
            Register:Register user: Passwords - very long
        '''
        email = u'email@wap.pl'
        post_data = {
            'email': email,
            'password': self.user_data['password'] * 10000,
            'confirm_password': self.user_data['password'] * 10000,
            'token': self.get_token('/register')
        }
        user = self.read_user(email)
        self.assertTrue(user is None)
        self.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        user = self.read_user(email)
        self.assertTrue(user is not None, 'User with very long password should be created')
        self.assertFalse(user.is_active, 'User should not have active account at this moment')

    def test_register_action_short_passwd(self):
        '''
            Register:Register user: Password - too short
        '''
        email = u'email@wap.pl'
        post_data = {
            'email': email,
            'password': '12',
            'confirm_password': self.user_data['password'] * 10000,
            'token': self.get_token('/register')
        }
        user = self.read_user(email)
        self.assertTrue(user is None)
        res = self.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        user = self.read_user(email)
        self.assertTrue(user is None, 'User with too short password should not be created')
        self.failUnless('<div class="control-group error">' in res)
        self.failUnless('Password is too short' in self.htmlToText(res.body))

    def test_register_action_empty_passwd(self):
        '''
            Register:Register user: Empty password
        '''
        email = u'email@wap.pl'
        post_data = {
            'email': email,
            'password': '',
            'confirm_password': self.user_data['password'] * 10000,
            'token': self.get_token('/register')
        }
        user = self.read_user(email)
        self.assertTrue(user is None)
        res = self.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        user = self.read_user(email)
        self.assertTrue(user is None, 'User with empty password should not be created')
        self.failUnless('<div class="control-group error">' in res)
        self.failUnless('Please enter your password' in self.htmlToText(res.body))

    def test_account_activation(self):
        '''
            Register:Activate user
        '''
        self.create_user()
        user = self.read_user(self.user_data['email'])

        res = self.app.get('/register/activate/' + user.activate_key)
        assert res
        user = self.read_user(self.user_data['email'])

        self.assertFalse(user.activate_key)
        self.assertTrue(user.is_active)
        self.assertTrue(user.activated_at)

        # check if login works after activation
        res = self.app.get('/login')
        self.assertTrue(len(res.headers['Set-Cookie']) > 150)
        res.form.set('email', self.user_data['email'])
        res.form.set('password', self.user_data['password'])
        res = res.form.submit()
        self.assertTrue(len(res.headers['Set-Cookie']) > 150)
        self.assertEqual(res.status, '302 Found')

    def test_account_activation_wrong_key(self):
        '''
            Register:Activate user
        '''
        self.create_user()
        user = self.read_user(self.user_data['email'])
        activate_key = user.activate_key
        res = self.app.get('/register/activate/' + activate_key[:-5], status=404)
        assert res
        user = self.read_user(self.user_data['email'])
        self.assertEqual(user.activate_key, activate_key)
        self.assertTrue(user.activate_key is not None)
        self.assertFalse(user.activated_at)
        self.assertFalse(user.is_active, 'User should not have active account at this moment')

    def test_account_activation_key_with_trash_chars(self):
        '''
            Register:Activate user
        '''
        from urllib import quote
        self.create_user()
        user = self.read_user(self.user_data['email'])
        activate_key = user.activate_key
        res = self.app.get('/register/activate/' + quote(
            u'ąśðłĸęł¶→łęóħó³→←śðđ[]}³½ĸżćŋðń→↓ŧ¶ħ→ĸł¼²³↓←ħ@ĸđśðĸ@ł¼ęłśħđó[³²½łðśđħ'.encode('utf-8')), status=404)
        assert res
        user = self.read_user(self.user_data['email'])
        self.assertEqual(user.activate_key, activate_key)
        self.assertTrue(user.activate_key is not None)
        self.assertFalse(user.activated_at)
        self.assertFalse(user.is_active, 'User should not have active account at this moment')


class RegisterNoPasswordTest(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self, {'env': 'np'})

    def test_register_action(self):
        '''
            Register:Register without password required
        '''
        post_data = {
            'email': self.user_data['email'],
            'token': self.get_token('/register')
        }
        user = self.read_user(self.user_data['email'])
        self.assertTrue(user is None)

        res = self.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        assert res
        user = self.read_user(self.user_data['email'])

        self.assertTrue(user is not None)
        self.assertEqual(user.email, post_data['email'], 'Emails should be the same')


class RegisterNoPassConfirm(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self, {'env': 'pc'})

    def test_no_pass_confirm(self):
        '''
            Register: Register without password confirm option
        '''

        post_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'] + u'sasasasa',
            'token': self.get_token('/register')
        }

        user = self.read_user(self.user_data['email'])
        self.assertTrue(user is None)
        res = self.app.post('/register', post_data, extra_environ={'REMOTE_ADDR': '0.0.0.0'})
        self.assertFalse('<div class="control-group error">' in res)
        self.assertFalse('<span class="help-inline">Passwords don&#39;t match!</span>' in res)
        user = self.read_user(self.user_data['email'])
        self.assertFalse(user is None, 'User profile should be created!')

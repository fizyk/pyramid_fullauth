# -*- coding: utf-8 -*-

import warnings
from HTMLParser import HTMLParser
from tests.utils import BaseTestSuite


class TestRegister(BaseTestSuite):

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

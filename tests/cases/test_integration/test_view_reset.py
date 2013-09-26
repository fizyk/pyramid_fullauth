# -*- coding: utf-8 -*-
from HTMLParser import HTMLParser

import transaction

from tests.utils import BaseTestSuite


class TestResetPassword(BaseTestSuite):

    def test_reset_view(self, base_app):
        '''Reset:view'''
        res = base_app.app.get('/password/reset')
        assert '<input type="email" placeholder="username@hostname.com" name="email" id="reset[email]"/>' in res

    def test_reset(self, base_app):
        '''Reset:Request Action get reset code'''
        self.create_user()
        user = self.read_user(self.user_data['email'])
        assert user.reset_key is None

        post_data = {
            'email': self.user_data['email'],
            'csrf_token': self.get_token('/password/reset', base_app.app)
        }
        res = base_app.app.post('/password/reset', post_data)
        assert res
        user = self.read_user(self.user_data['email'])
        assert user.reset_key is not None

    def test_reset_wrong(self, base_app):
        '''Reset:Request Action with wrong email'''
        self.create_user()
        self.read_user(self.user_data['email'])

        post_data = {
            'email': u'wrong@example.com',
            'csrf_token': self.get_token('/password/reset', base_app.app)
        }
        res = base_app.app.post('/password/reset', post_data)
        assert '<div class="alert alert-error">Error! User does not exists</div>' in res

    def test_reset_proceed(self, base_app):
        '''Reset test for reseting pasword'''

        self.create_user()
        user = self.read_user(self.user_data['email'])
        user.set_reset()
        transaction.commit()

        user = self.read_user(self.user_data['email'])
        res = base_app.app.get(str('/password/reset/' + user.reset_key))
        assert 'Recover your password - choose new password' in res

        post_data = {
            'password':
            self.user_data['password'],
            'confirm_password':
            self.user_data['password'],
            'csrf_token':
            self.get_token('/password/reset', base_app.app)
        }
        res = base_app.app.post(str('/password/reset/' + user.reset_key), post_data)
        assert res

        user = self.read_user(self.user_data['email'])
        assert user.reset_key is None

    def test_reset_proceed_wrong(self, base_app):
        '''Reset test for reseting pasword with notmatched passwords'''
        self.create_user()
        user = self.read_user(self.user_data['email'])
        user.set_reset()
        transaction.commit()

        user = self.read_user(self.user_data['email'])
        res = base_app.app.get(str('/password/reset/' + user.reset_key))
        assert 'Recover your password - choose new password' in res

        post_data = {
            'password':
            self.user_data['password'],
            'confirm_password':
            self.user_data['password'] + u'sasasa',
            'csrf_token':
            self.get_token('/password/reset', base_app.app)
        }
        res = base_app.app.post(str('/password/reset/' + user.reset_key), post_data)
        assert 'Error! Password doesn\'t match' in HTMLParser().unescape(res.body)

    def test_reset_proceed_wrong_csrf(self, base_app):
        '''Reset test for reseting pasword with notmatched csrf'''

        self.create_user()
        user = self.read_user(self.user_data['email'])
        user.set_reset()
        transaction.commit()

        user = self.read_user(self.user_data['email'])
        res = base_app.app.get(str('/password/reset/' + user.reset_key))
        assert 'Recover your password - choose new password' in res

        post_data = {
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'],
            'csrf_token': self.get_token('/password/reset', base_app.app) + '1'
        }
        res = base_app.app.post(str('/password/reset/' + user.reset_key),
                                post_data, status=401)

# -*- coding: utf-8 -*-

import transaction

from tests import BaseTestCase


class ResetPasswordTest(BaseTestCase):

    def test_reset_view(self):
        '''Reset:view'''
        res = self.app.get('/password/reset')
        self.failUnless(
            '<input type="email" placeholder="username@hostname.com" name="email" id="reset[email]"/>' in res)

    def test_reset(self):
        '''Reset:Request Action get reset code'''
        self.create_user()
        user = self.read_user(self.user_data['email'])
        self.assertTrue(user.reset_key is None)

        post_data = {
            'email': self.user_data['email'],
            'token': self.get_token('/password/reset')
        }
        res = self.app.post('/password/reset', post_data)
        assert res
        user = self.read_user(self.user_data['email'])
        self.assertTrue(user.reset_key is not None)

    def test_reset_wrong(self):
        '''Reset:Request Action with wrong email'''
        self.create_user()
        self.read_user(self.user_data['email'])

        post_data = {
            'email': u'wrong@example.com',
            'token': self.get_token('/password/reset')
        }
        res = self.app.post('/password/reset', post_data)
        self.failUnless('<div class="alert alert-error">Error! User does not exists</div>' in res)

    def test_reset_proceed(self):
        '''Reset test for reseting pasword'''

        self.create_user()
        user = self.read_user(self.user_data['email'])
        user.set_reset()
        transaction.commit()

        user = self.read_user(self.user_data['email'])
        res = self.app.get(str('/password/reset/' + user.reset_key))
        self.failUnless('<h1>Recover your password - choose new password</h1>' in res)

        post_data = {
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'],
            'token': self.get_token('/password/reset')
        }
        res = self.app.post(str('/password/reset/' + user.reset_key), post_data)
        assert res
        print res

        user = self.read_user(self.user_data['email'])
        self.assertTrue(user.reset_key is None)

    def test_reset_proceed_wrong(self):
        '''Reset test for reseting pasword with notmatched passwords'''

        self.create_user()
        user = self.read_user(self.user_data['email'])
        user.set_reset()
        transaction.commit()

        user = self.read_user(self.user_data['email'])
        res = self.app.get(str('/password/reset/' + user.reset_key))
        self.failUnless('<h1>Recover your password - choose new password</h1>' in res)

        post_data = {
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'] + u'sasasa',
            'token': self.get_token('/password/reset')
        }
        res = self.app.post(str('/password/reset/' + user.reset_key), post_data)
        self.failUnless('<div class="alert alert-error">Error! Password doesn&#39;t match</div>' in res)

    def test_reset_proceed_wrong_csrf(self):
        '''Reset test for reseting pasword with notmatched csrf'''

        self.create_user()
        user = self.read_user(self.user_data['email'])
        user.set_reset()
        transaction.commit()

        user = self.read_user(self.user_data['email'])
        res = self.app.get(str('/password/reset/' + user.reset_key))
        self.failUnless('<h1>Recover your password - choose new password</h1>' in res)

        post_data = {
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'],
            'token': self.get_token('/password/reset') + '1'
        }
        res = self.app.post(str('/password/reset/' + user.reset_key), post_data)
        self.failUnless('CSRF token did not match' in res)

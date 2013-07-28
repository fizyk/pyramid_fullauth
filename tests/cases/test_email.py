# -*- coding: utf-8 -*-

import transaction
import warnings
from tests import BaseTestCase
import unittest


class PasswordTest(BaseTestCase):

    def test_email_view_not_logged(self):
        '''Change Email:view user not logged in'''
        res = self.app.get('/email/change')
        self.failUnless(res.status == '302 Found')
        self.failUnless(res.location == 'http://localhost/login?after=%2Femail%2Fchange')

    def test_email_view_logged(self):
        '''Change Email:view user logged in'''

        self.create_user({'is_active': True})
        # login user
        self.authenticate()

        res = self.app.get('/email/change')
        self.failUnless(
            '<input type="email" placeholder="username@hostname.com" name="email" id="change[email]"/>' in res)

    def test_email_valid_view(self):
        '''Change Email:view Valid data'''

        self.create_user({'is_active': True})
        # login user
        self.authenticate()

        email = self.user_data['email']
        user = self.read_user(email)
        new_email = 'email@email.com'
        post_data = {
            'email': new_email,
            'token': self.get_token('/email/change')
        }
        res = self.app.post('/email/change', post_data)
        assert res
        transaction.commit()

        user = self.read_user(email)
        self.assertTrue(user.new_email == new_email)
        self.assertTrue(user.email == email)
        self.assertTrue(user.email_change_key is not None)

    def test_email_wrong_email_view(self):
        '''Change Email:view Wrong email'''

        self.create_user({'is_active': True})
        # login user
        self.authenticate()

        email = self.user_data['email']
        user = self.read_user(email)
        new_email = 'email.email.com'
        post_data = {
            'email': new_email,
            'token': self.get_token('/email/change')
        }
        res = self.app.post('/email/change', post_data)
        self.failUnless('<div class="alert alert-error">Error! Incorrect e-mail format</div>' in res)

    def test_email_proceed(self):
        '''Change Email:changing email'''

        self.create_user({'is_active': True})
        # login user
        self.authenticate()

        user = self.read_user(self.user_data['email'])
        new_email = u'email2@email.com'
        user.set_new_email(new_email)
        transaction.commit()

        user = self.read_user(self.user_data['email'])
        res = self.app.get(str('/email/change/' + user.email_change_key))
        self.failUnless(res.status == '302 Found')

        user = self.read_user(self.user_data['email'])
        self.assertTrue(user is None)  # there is no user with old email

        user = self.read_user(new_email)
        self.assertTrue(user.email_change_key is None)

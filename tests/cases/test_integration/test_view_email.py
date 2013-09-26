
import transaction

from tests.utils import BaseTestSuite


class TestEmail(BaseTestSuite):

    def test_email_view_not_logged(self, base_app):
        '''Change Email:view user not logged in'''
        res = base_app.app.get('/email/change')
        assert res.status == '302 Found'
        assert res.location == 'http://localhost/login?after=%2Femail%2Fchange'

    def test_email_view_logged(self, base_app):
        '''Change Email:view user logged in'''

        self.create_user({'is_active': True})
        # login user
        self.authenticate(base_app.app)

        res = base_app.app.get('/email/change')
        assert '<input type="email" placeholder="username@hostname.com" name="email" id="change[email]"/>' in res

    def test_email_valid_view(self, base_app):
        '''Change Email:view Valid data'''

        self.create_user({'is_active': True})
        # login user
        self.authenticate(base_app.app)

        email = self.user_data['email']
        user = self.read_user(email)
        new_email = 'email@email.com'
        post_data = {
            'email': new_email,
            'csrf_token': self.get_token('/email/change', base_app.app)
        }
        res = base_app.app.post('/email/change', post_data)
        assert res
        transaction.commit()

        user = self.read_user(email)
        assert user.new_email == new_email
        assert user.email == email
        assert user.email_change_key

    def test_email_wrong_email_view(self, base_app):
        '''Change Email:view Wrong email'''

        self.create_user({'is_active': True})
        # login user
        self.authenticate(base_app.app)

        email = self.user_data['email']
        user = self.read_user(email)
        new_email = 'email.email.com'
        post_data = {
            'email': new_email,
            'csrf_token': self.get_token('/email/change', base_app.app)
        }
        res = base_app.app.post('/email/change', post_data)
        assert 'Error! Incorrect e-mail format' in res

    def test_email_proceed(self, base_app):
        '''Change Email:changing email'''

        self.create_user({'is_active': True})
        # login user
        self.authenticate(base_app.app)

        user = self.read_user(self.user_data['email'])
        new_email = u'email2@email.com'
        user.set_new_email(new_email)
        transaction.commit()

        user = self.read_user(self.user_data['email'])
        res = base_app.app.get(str('/email/change/' + user.email_change_key))
        assert res.status == '302 Found'

        user = self.read_user(self.user_data['email'])
        assert user is None  # there is no user with old email

        user = self.read_user(new_email)
        assert not user.email_change_key

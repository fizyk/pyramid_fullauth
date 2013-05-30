# -*- coding: utf-8 -*-
'''
Created on 18-07-2012

@author: sliwinski
'''
import warnings
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from pyramid_fullauth.models import User, Base


class BaseTest(unittest.TestCase):

    '''Basic test class, to be used in data model tests'''

    user_data = {'password': u'password1',
                 'email': u'test@example.com',
                 'address_ip': u'32.32.32.32'}

    def setUp(self):
        '''
            setUp test method @see unittest.TestCase.setUp
        '''
        connection = 'sqlite://'

        engine = create_engine(connection, echo=False)

        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.session = sessionmaker(bind=engine)()
        self.engine = engine

    def tearDown(self):
        '''
            This tears tests down
        '''

        # Lets drop tables after test, so we don't have any problem if model changes
        Base.metadata.drop_all(self.engine)
        self.session.close()
        del self.engine

    def create_user(self, **user_data):
        '''method to create basic user'''
        user = User()

        for key in self.user_data:
            if not key in user_data:
                user_data[key] = self.user_data[key]

        for key in user_data.keys():
            setattr(user, key, user_data[key])

        self.session.add(user)
        self.session.commit()


class UserValidateTest(BaseTest):

    '''
        User model implementation tests
    '''

    def setUp(self):
        BaseTest.setUp(self)

    def test_email_valid_formats(self):
        ''' Check all valid formats of Email (RFC 5321) can be set by user
        '''
        emails = (
            u'very.common@example.com',
            u'a.little.lengthy.but.fine@dept.example.com',
            u'disposable.style.email.with+symbol@example.com',
            u'"very.unusual.@.unusual.com"@example.com',
            u'!#$%&\'*+-/=?^_`{}|~@example.org',
            u'""@example.org',
            u'"much.more unusual"@example.com',
            u'"()<>[]:,;@\\\"!#$%&\'*+-/=?^_`{}| ~  ? ^_`{}|~.a"@example.org',
            #            TODO: make listed below validateable too
            # u'postbox@com',  # (top-level domains are valid hostnames)
            # u'user@[IPv6:2001:db8:1ff::a0b:dbd0]',
            # u'"very.(),:;<>[]\".VERY.\"very@\\ \"very\".unusual"@strange.example.com',
        )
        self.create_user(username=u'u1')

        user = self.session.query(User).filter(User.username == u'u1').one()
        self.assertEqual(user.email, u'test@example.com')

        for email in emails:
            try:
                user.email = email
                self.session.commit()
            except AttributeError:
                raise AttributeError('email: {0} did not validate'.format(email))
            user = self.session.query(User).filter(User.username == u'u1').one()
            self.assertEqual(user.email, email)

    def test_email_invalid_formats(self):
        ''' Check all invalid formats of Email (RFC 5321) can not be set by user
        '''
        emails = (
            'Abc.example.com'  # (an @ character must separate the local and domain parts)
            'Abc.@example.com'  # (character dot(.) is last in local part)
            'Abc..123@example.com'  # (character dot(.) is double)
            'A@b@c@example.com'  # (only one @ is allowed outside quotation marks)
            'a"b(c)d,e:f;g<h>i[j\k]l@example.com'  # (none of the special characters in this local part is allowed outside quotation marks)
            'just"not"right@example.com'  # (quoted strings must be dot separated, or the only element making up the local-part)
            'this is"not\allowed@example.com'  # (spaces, quotes, and backslashes may only exist when within quoted strings and preceded by a backslash)
            'this\ still\"not\\allowed@example.com'  # (even if escaped (preceded by a backslash), spaces, quotes, and backslashes must still be contained by quotes)
        )

        self.create_user(username=u'u1')

        user = self.session.query(User).filter(User.username == u'u1').one()
        self.assertEqual(user.email, u'test@example.com')

        for email in emails:
            with self.assertRaises(AttributeError):
                user.email = email
                self.session.commit()
            user = self.session.query(User).filter(User.username == u'u1').one()
            self.assertEqual(user.email, u'test@example.com')

    def test_validate_email_bad(self):
        '''User::validate e-mail::bad'''

        user = User()
        self.assertRaises(AttributeError, lambda: setattr(user, "email", u'bad-mail'))

    def test_validate_email_ok(self):
        '''User::validate e-mail::ok'''

        user = User()
        email = u"test@test.info"
        user.email = email
        self.assertEqual(user.email, email, 'email is {0}, user has {1} email'.format(email, user.email))

    def test_address_ip_valid(self):
        ''' Check all valid ip addresses can be set by system to user model
        '''
        ips = (
            u'32.32.32.32',
            u'2001:cdba:0000:0000:0000:0000:3257:9652',
            u'2001:cdba:0:0:0:0:3257:9652',
            u'2001:cdba::3257:9652',
        )

        self.create_user(username=u'u1')

        user = self.session.query(User).filter(User.username == u'u1').one()
        self.assertEqual(user.email, u'test@example.com')

        for ip in ips:
            try:
                user.address_ip = ip
                self.session.commit()
            except AttributeError:
                raise AttributeError('ip: {0} did not validate'.format(ip))
            user = self.session.query(User).filter(User.username == u'u1').one()
            self.assertEqual(user.address_ip, ip)

    @unittest.skip('No ip validation yet implemented')
    def test_address_ip_invalid(self):
        '''Check invalid (RFC 3330: private, testing, special purposes) IP
        addresses can not be set by system to user model

        TODO
        '''
        ips = (
            '0.0.0.1',  # Addresses in this block refer to source hosts on "this" network.
            '0.0.1.123',  # Addresses in this block refer to source hosts on "this" network.
            '0.10.10.120',  # Addresses in this block refer to source hosts on "this" network.
            '10.0.0.1',  # This block is set aside for use in private networks
            '10.1.2.3',  # This block is set aside for use in private networks
            '24.0.0.1',
            # This block was allocated in early 1996 for use in provisioning IP
            # service over cable television systems
            '39.0.0.1',  # This block was used in the "Class A Subnet Experiment" that commenced in May 1995
            '127.0.0.1',  # This block is assigned for use as the Internet host loopback address
            '128.0.0.1',
            # This block, corresponding to the numerically lowest of the former Class
            # B addresses, was initially and is still reserved by the IANA.
            '169.254.0.1',
            # This is the "link local" block.  It is allocated for communication between hosts on a single link
            '172.16.0.1',  # This block is set aside for use in private networks
            '191.255.0.1',
            # This block, corresponding to the numerically highest to the former Class
            # B addresses, was initially and is still reserved by the IANA.
            '192.0.0.1',
            # This block, corresponding to the numerically lowest of the former Class
            # C addresses, was initially and is still reserved by the IANA.
            '192.0.2.1',  # This block is assigned as "TEST-NET" for use in documentation and example code.
            '192.88.99.1',  # This block is allocated for use as 6to4 relay anycast addresses
            '192.168.0.1',  # This block is set aside for use in private networks
            '198.18.0.1',  # This block has been allocated for use in benchmark tests of network interconnect devices
            '223.255.255.1',
            # This block, corresponding to the numerically highest of the former Class
            # C addresses, was initially and is still reserved by the IANA.
            '255.255.255.255',  # Multicast address
        )
        user = User()
        user.username = u'u1'
        user.password = u'password1'
        user.email = u'test@example.com'
        user.address_ip = u'32.32.32.32'

        self.session.add(user)
        self.session.commit()
        user = self.session.query(User).filter(User.username == u'u1').one()
        self.assertEqual(user.email, u'test@example.com')

        for ip in ips:
            with self.assertRaises(AttributeError):
                user.address_ip = ip
                self.session.commit()
            user = self.session.query(User).filter(User.username == u'u1').one()
            self.assertEqual(user.address_ip, u'32.32.32.32')


class UserReprTest(BaseTest):

    def test_introduce_email(self):
        '''user gets introduced by e-mail only'''
        user = User()
        user.email = u'test@test.pl'
        self.assertEqual(str(user), 'test@...', 'To string should return concatenated email')

    def test_introduce_username(self):
        '''user gets introduced by username'''
        user = User()
        self.assertEqual(str(user), 'None', 'User not saved should be represented by \'None\'')
        user.id = 1
        self.assertEqual(str(user), '1', 'User with id=1 should be represented by \'1\'')

        user.email = u'test@test.pl'
        user.username = u'testowy'
        self.assertEqual(str(user), 'testowy', 'To string should return username')
        self.assertEqual(user.__repr__(), "<User ('1', 'testowy')>",
                         'User should be represented by "<User (\'1\', \'testowy\')>"')


class PasswordTest(BaseTest):

    '''
        User implementation tests
    '''

    def setUp(self):
        BaseTest.setUp(self)
        self.create_user(username=u'u1')

    def test_hash_checkout(self):
        '''User::check_password()'''

        user = self.session.query(User).filter(User.username == u'u1').one()
        self.assertTrue(user.check_password(u'password1'))

    def test_password_change(self):
        '''User::password change'''

        new_password = u'haselko'

        user = self.session.query(User).filter(User.username == u'u1').one()
        old_password = user.password
        old_salt = user._salt
        user.password = new_password
        self.session.commit()

        user = self.session.query(User).filter(User.username == u'u1').one()
        self.assertFalse(user.password == old_password, 'Passwords should be different!')
        self.assertFalse(user._salt == old_salt, 'Salt has not changed!')
        self.assertTrue(user.check_password(new_password), 'User password is different that excepted!')

    def test_password_empty(self):
        '''User::empty password change'''

        def empty_pass():
            user = self.session.query(User).filter(User.username == u'u1').one()
            user.password = u''
            self.session.commit()

        self.assertRaises(ValueError, empty_pass)

    def test_password_very_long(self):
        '''User::password change long'''

        new_password = u'haselko' * 10000

        user = self.session.query(User).filter(User.username == u'u1').one()
        old_password = user.password
        old_salt = user._salt
        user.password = new_password
        self.session.commit()

        user = self.session.query(User).filter(User.username == u'u1').one()
        self.assertFalse(user.password == old_password, 'Passwords should be different!')
        self.assertFalse(user._salt == old_salt, 'Salt has not changed!')
        self.assertTrue(user.check_password(new_password), 'User password is different that excepted!')


class AdminTest(BaseTest):

    '''
        Admin implemetation tests
    '''

    def setUp(self):
        BaseTest.setUp(self)
        self.create_user(username=u'u1')

    def test_regular_user_not_admin(self):
        '''Regular user is_admin flag test
        '''

        user = self.session.query(User).filter(User.username == u'u1').one()
        self.assertFalse(user.is_admin, 'Default user should have flag is_admin equal False')

    def test_regular_user_admin(self):
        '''Admin user is_admin flag test'''

        user = self.session.query(User).filter(User.username == u'u1').one()
        user.is_admin = True
        self.session.commit()

        user = self.session.query(User).filter(User.username == u'u1').one()
        self.assertTrue(user.is_admin, 'Admin user should have flag is_admin equal True')

    def test_remove_last_admin(self):
        '''Admin user is_admin flag test'''

        user = self.session.query(User).filter(User.username == u'u1').one()
        user.is_admin = True
        self.session.commit()

        def remove_is_admin():
            user.is_admin = False

        self.assertRaises(AttributeError, remove_is_admin)
        self.session.commit()

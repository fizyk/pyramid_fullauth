# -*- coding: utf-8 -*-

'''
    | Models needed for registration, and user servicing.
    | Contains basic user definition
'''

import re
import uuid

from sqlalchemy import Column
from sqlalchemy import Unicode
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Boolean
from sqlalchemy import Sequence
from sqlalchemy import DateTime
from sqlalchemy import Table
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.event import listen
from sqlalchemy.orm import validates
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import object_session
from sqlalchemy.orm.util import has_identity

from pyramid_basemodel import Base
from pyramid_fullauth import exceptions
from pyramid_fullauth.models.mixins import PasswordMixin
from datetime import datetime

pattern_mail = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]{0,256}(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+){0,256}"  # dot-atom
    # quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177 ]|\\[\001-\011\013\014\016-\177 ]){0,256}"'
    r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2}\.?)$)'  # domain
    r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE)  # literal form, ipv4 address (SMTP 4.1.3)


class User(PasswordMixin, Base):

    '''
        User object/mapper
    '''

    __tablename__ = 'users'
    __pattern_mail = pattern_mail

    id = Column(Integer, Sequence(__tablename__ + '_sq'), primary_key=True)
    username = Column(Unicode(32), unique=True, nullable=True)
    firstname = Column(Unicode(100), nullable=True)
    lastname = Column(Unicode(100), nullable=True)
    email = Column(Unicode(254), unique=True, nullable=False)  # RFC5321 and RFC3696(errata)
    activate_key = Column(String(255), default=lambda: str(uuid.uuid4()), unique=True)
    address_ip = Column(String(15), nullable=False)

    registered_at = Column(DateTime, default=func.now(), nullable=False)
    logged_at = Column(DateTime, default=func.now(), nullable=False)
    activated_at = Column(DateTime, nullable=True)
    deactivated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    is_admin = Column(Boolean, default=False, nullable=False)
    new_email = Column(Unicode(254), unique=True, nullable=True)  # RFC5321 and RFC3696(errata)
    email_change_key = Column(String(255), default=None, unique=True)

    @property
    def is_active(self):
        """
        User's active status.

        :returns: Returns False if user account is not active (or deleted).
        :rtype: bool
        """
        return not (self.deactivated_at or self.deleted_at or self.activate_key) and (self.activated_at is not None)

    @is_active.setter
    def is_active(self, value):
        """is_active property setter.

        If set to True - removes deactivated_at, deleted_at, activate_key and set activated_at to datetime now
        If set to False - set deactivated_at to now and activated_at to None
        """

        # Allow to modify this only if object is in the persistent state to prevent "default values" errors/bugs.
        # http://stackoverflow.com/questions/3885601/sqlalchemy-get-object-instance-state
        if object_session(self) is not None and has_identity(self):
            if value:
                self.deactivated_at = None
                self.deleted_at = None
                self.activate_key = None
                self.activated_at = datetime.now()
            else:
                self.deactivated_at = datetime.now()
                self.activated_at = None
        else:
            raise AttributeError('User has to be in the persistent state - stored in the DB')

    @is_active.deleter
    def is_active(self):
        """is_active property deleter
        """
        pass

    def provider_id(self, provider):
        provider_id = None
        for user_provider in self.providers:
            if user_provider.provider == provider:
                provider_id = user_provider.provider_id
                break

        return provider_id

    def __repr__(self):
        return "<User ('{0}', '{1}')>".format(self.id, str(self))

    def __unicode__(self):
        if self.username:
            return self.username
        elif self.email:
            return self.email.split('@')[0] + '@...'
        else:
            return str(self.id)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    @validates('email', 'new_email')
    def validate_email(self, key, address):
        '''
            Validates email address

            .. note::

                More about simple validators: http://docs.sqlalchemy.org/en/latest/orm/mapper_config.html#simple-validators

            :raises AttributeError: Information about an error
        '''
        if address:
            if pattern_mail.match(address):
                return address
            else:
                raise AttributeError('Incorrect e-mail format')

        raise AttributeError('E-mail is empty')

    @validates('is_admin')
    def validate_is_admin(self, key, value):
        '''
            Validates is_admin value, we forbid the deletion of the last superadmin.

            .. note::

                More about simple validators: http://docs.sqlalchemy.org/en/latest/orm/mapper_config.html#simple-validators

            :raises AttributeError: Information about an error
        '''

        if self.is_admin and not value:
            admin_counter = object_session(self).query(User).filter(
                User.is_admin == True, User.deleted_at == None).count()
            if admin_counter and admin_counter <= 1:
                raise AttributeError('Can\'t delete last superadmin!')
        return value

    def delete(self):
        '''
            Performs soft delete action. along with checking if it's super admin, or not

            :rises redsky.pyramid.registerlogin.exceptions.DeleteException: if you try to delete last super admin.

            .. note::
                You should use this method to delete users
        '''

        if self.is_admin:
            admin_counter = object_session(self).query(User).filter(
                User.is_admin == True, User.deleted_at == None).count()
            if admin_counter and admin_counter <= 1:
                raise exceptions.DeleteException('Can\'t delete last superadmin!')

        self.deleted_at = datetime.now()

    def set_new_email(self, email_new):
        '''
            Set new email and generate new email change hash
        '''
        self.new_email = email_new
        self.email_change_key = str(uuid.uuid4())

    def change_email(self):
        '''
            Change email after activation
            We don't clear new email field because of validator of email which won't allow to None value.
        '''
        self.email = self.new_email
        self.email_change_key = None


class Group(Base):

    '''
        User group object/mapper
    '''
    __tablename__ = 'groups'

    id = Column(Integer, Sequence(__tablename__ + '_sq'), primary_key=True)
    name = Column(Unicode(100), unique=True, nullable=False)

    #: Relation to User object
    users = relationship(User, secondary=lambda: user_group, backref='groups')


class AuthenticationProvider(Base):

    '''
        Model to store authentication methods for different providers
    '''
    __tablename__ = 'user_authentication_provider'

    __table_args__ = (UniqueConstraint('provider', 'provider_id', name='user_authentication_methods_provider_id'),)

    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    provider = Column(Unicode(15), primary_key=True)
    provider_id = Column(String(255), nullable=False)

    user = relationship(User, lazy='load', backref='providers')

#: Association table between User and Group models.
user_group = Table('users_groups', Base.metadata,
                   Column('user_id', Integer, ForeignKey(User.id), primary_key=True),
                   Column('group_id', Integer, ForeignKey(Group.id), primary_key=True)
                   )

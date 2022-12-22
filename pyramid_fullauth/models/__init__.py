# Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Models needed for registration, and user servicing."""

import sys
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    Unicode,
    String,
    Integer,
    Boolean,
    Sequence,
    DateTime,
    Table,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import validates, relationship
from sqlalchemy.orm.session import object_session
from sqlalchemy.orm.util import has_identity
from pyramid_basemodel import Base

from pyramid_fullauth import exceptions
from pyramid_fullauth.models.mixins import UserPasswordMixin, UserEmailMixin


class User(UserPasswordMixin, UserEmailMixin, Base):
    """User object."""

    __tablename__ = "users"

    id = Column(Integer, Sequence(__tablename__ + "_sq"), primary_key=True)
    username = Column(Unicode(32), unique=True, nullable=True)
    firstname = Column(Unicode(100), nullable=True)
    lastname = Column(Unicode(100), nullable=True)
    activate_key = Column(String(255), default=lambda: str(uuid.uuid4()), unique=True)
    address_ip = Column(String(15), nullable=False)

    registered_at = Column(DateTime, default=func.now(), nullable=False)
    logged_at = Column(DateTime, default=func.now(), nullable=False)
    activated_at = Column(DateTime, nullable=True)
    deactivated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    is_admin = Column(Boolean, default=False, nullable=False)

    @property
    def is_active(self):
        """
        Check if user is active.

        :returns: Returns False if user account is not active (or deleted).
        :rtype: bool

        """
        return not (self.deactivated_at or self.deleted_at or self.activate_key) and bool(self.activated_at)

    @is_active.setter
    def is_active(self, value):
        """
        Set user as active/inactive.

        :param bood value:
            True - removes deactivated_at, deleted_at, activate_key and set activated_at to datetime now
            False - set deactivated_at to now and activated_at to None

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
            raise AttributeError("User has to be in the persistent state - stored in the DB")

    def provider_id(self, provider):
        """
        Return provider identification for give user.

        :param str provider: provider name
        :returns: provider identification
        :rtype: str

        """
        for user_provider in self.providers:
            if user_provider.provider == provider:
                return user_provider.provider_id
        return None

    def __repr__(self):
        """Object representation."""
        return f"<User ('{self.id}')>"

    def __unicode__(self):
        """Unicode cast rules."""
        if self.username:
            return self.username
        if self.email:
            return self.email.split("@")[0] + "@..."
        return str(self.id)

    def __str__(self):  # pragma: no cover
        """Stringified user representation."""
        if sys.version[0] == "3":
            return self.__unicode__()
        return self.__unicode__().encode("utf-8")

    @validates("is_admin")
    def validate_is_admin(self, _, value):
        """
        Validate is_admin value, we forbid the deletion of the last superadmin.

        .. note::

            More about simple validators: http://docs.sqlalchemy.org/en/latest/orm/mapper_config.html#simple-validators

        :raises AttributeError: Information about an error

        """
        if self.is_admin and not value:
            admin_counter = object_session(self).query(User).filter(User.is_admin, User.deleted_at.is_(None)).count()
            if admin_counter and admin_counter <= 1:
                raise AttributeError("Can't delete last superadmin!")
        return value

    def delete(self):
        """
        Perform soft delete action. along with checking if it's super admin, or not.

        :rises pyramid_fullauth.exceptions.DeleteException: if you try to delete last super admin.

        .. note::
            You should use this method to delete users

        """
        if self.is_admin:
            admin_counter = object_session(self).query(User).filter(User.is_admin, User.deleted_at.is_(None)).count()
            if admin_counter and admin_counter <= 1:
                raise exceptions.DeleteException("Can't delete last superadmin!")

        self.deleted_at = datetime.now()


class Group(Base):
    """User group object."""

    __tablename__ = "groups"

    id = Column(Integer, Sequence(__tablename__ + "_sq"), primary_key=True)
    name = Column(Unicode(100), unique=True, nullable=False)

    #: Relation to User object
    users = relationship(User, secondary=lambda: user_group, backref="groups")


class AuthenticationProvider(Base):
    """Model to store authentication methods for different providers."""

    __tablename__ = "user_authentication_provider"

    __table_args__ = (UniqueConstraint("provider", "provider_id", name="user_authentication_methods_provider_id"),)

    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    provider = Column(Unicode(15), primary_key=True)
    provider_id = Column(String(255), nullable=False)

    user = relationship(User, backref="providers")


#: Association table between User and Group models.
user_group = Table(  # pylint:disable=invalid-name
    "users_groups",
    Base.metadata,
    Column("user_id", Integer, ForeignKey(User.id), primary_key=True),
    Column("group_id", Integer, ForeignKey(Group.id), primary_key=True),
)

# Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Password mixin related module."""

import os
import hashlib
from hashlib import algorithms_guaranteed
import uuid

from sqlalchemy import Column
from sqlalchemy import Unicode
from sqlalchemy import Enum
from sqlalchemy import String
from sqlalchemy.orm import validates
from pyramid_fullauth.exceptions import EmptyError


class UserPasswordMixin(object):
    """Authentication field definition along with appropriate methods."""

    #: password field
    password = Column(Unicode(128), nullable=False)

    #: hash_algorithm field
    _hash_algorithm = Column(
        "hash_algorithm",
        Enum(*algorithms_guaranteed, name="hash_algorithms_enum"),
        default="sha256",
        nullable=False,
    )

    #: salt field
    _salt = Column("salt", Unicode(128), nullable=False)

    #: reset key field
    reset_key = Column(String(255), unique=True)

    def check_password(self, password):
        """
        Check if password correspond to the saved one.

        :param str password: password to compare

        :returns: True, if password is same, False if not
        :rtype: bool
        """
        if password and self.hash_password(password, self._salt, self._hash_algorithm) == self.password:
            return True

        return False

    def set_reset(self):
        """Generate password reset key."""
        self.reset_key = str(uuid.uuid4())

    @classmethod
    def hash_password(cls, password, salt, hash_method):
        """
        Produce hash out of a password.

        :param str password: password string, not hashed
        :param str salt: salt
        :param callable hash_method: a hash method which will be used to generate hash

        :returns: hashed password
        :rtype: str

        """
        # let's allow passing just method name
        if not callable(hash_method):
            hash_method = getattr(hashlib, hash_method)

        # let's convert password to bytest from string
        if isinstance(password, str):
            password = password.encode("utf-8")

        #  to bytest from string
        if isinstance(salt, str):
            salt = salt.encode("utf-8")

        # generating salted hash
        return hash_method(password + salt).hexdigest()

    @validates("password")
    def password_validator(self, _, password):
        """
        Validate password.

        Password validator keeps new password hashed.
        Rises Value error on empty password

        :param str key: field key
        :param str password: new password

        :returns: hashed and salted password
        :rtype: str
        :raises: pyramid_fullauth.exceptions.EmptyError

        .. note::

            If you're using this Mixin on your own User object,
            don't forget to add a listener as well, like that:

            .. code-block:: python

                from sqlalchemy.event import listen

                listen(User.password, 'set', User.password_listener, retval=True)

        .. note::

            For more information on Attribute Events in sqlalchemy see:

            :meth:`sqlalchemy.orm.events.AttributeEvents.set`

        """
        if not password:
            raise EmptyError("password-empty")

        # reading default hash_algorithm
        # pylint:disable=protected-access
        hash_algorithm = self.__class__._hash_algorithm.property.columns[0].default.arg
        # pylint:enable=protected-access

        # getting currently used hash method
        hash_method = getattr(hashlib, hash_algorithm)

        # generating salt
        salt = hash_method()
        salt.update(os.urandom(60))
        salt_value = salt.hexdigest()

        # storing used hash algorithm
        self._hash_algorithm = hash_algorithm
        self._salt = salt_value
        return self.__class__.hash_password(password, salt_value, hash_method)

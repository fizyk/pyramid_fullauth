# Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Email mixin related module."""

import re
import uuid

from sqlalchemy import Column, Unicode, String
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property


from pyramid_fullauth.exceptions import EmptyError, EmailValidationError
from pyramid_fullauth.models.extensions import CaseInsensitive

PATTERN_MAIL = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]{0,256}(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+){0,256}"  # dot-atom
    # quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177 ]|\\[\001-\011\013\014\016-\177 ]){0,256}"'
    r")@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2}\.?)$)"  # domain
    # literal form, ipv4 address (SMTP 4.1.3)
    r"|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$",
    re.IGNORECASE,
)


class UserEmailMixin(object):
    """User email fields and functionality."""

    _email = Column("email", Unicode(254), unique=True, nullable=False)  # RFC5321 and RFC3696(errata)
    _new_email = Column("new_email", Unicode(254), unique=True, nullable=True)  # RFC5321 and RFC3696(errata)
    email_change_key = Column(String(255), default=None, unique=True)

    def __init__(self, *args, **kwargs):
        """Switch possible email and new_email kwarg into new column attribute names."""
        if "email" in kwargs:
            kwargs["_email"] = kwargs.pop("email")
        if "new_email" in kwargs:
            kwargs["_new_email"] = kwargs.pop("new_email")

        super().__init__(*args, **kwargs)

    @hybrid_property
    def email(self):
        """Email field getter."""
        if self._email:
            return self._email.lower()
        return self._email

    @email.setter
    def email(self, value):
        """Email field setter."""
        if value:
            value = value.lower()
        self._email = value

    @email.comparator
    def email(cls):  # pylint:disable=no-self-argument,method-hidden
        """Email field comparator."""
        return CaseInsensitive(cls._email)

    @hybrid_property
    def new_email(self):
        """Email field getter."""
        if self._new_email:
            return self._new_email.lower()
        return self._new_email

    @new_email.setter
    def new_email(self, value):
        """Email field setter."""
        if value:
            value = value.lower()
        self._new_email = value

    @new_email.comparator
    def new_email(cls):  # pylint:disable=no-self-argument,method-hidden
        """Email field comparator."""
        return CaseInsensitive(cls._new_email)

    @validates("_email", "_new_email")
    def validate_email(self, _, address):
        """
        Validate email addresses.

        .. note::

            See pyramid docs about
            `simple validators <http://docs.sqlalchemy.org/en/latest/orm/mapper_config.html#simple-validators>`_

        :param str key: field key
        :param str address: email address

        :raises EmailValidationError:
        :raises EmptyError:
        """
        if address:
            if PATTERN_MAIL.match(address):
                return address

            raise EmailValidationError("Incorrect e-mail format")

        raise EmptyError("E-mail is empty")

    def set_new_email(self, email_new):
        """
        Set new email and generate new email change hash.

        :param str email_new: email address

        :returns: generated email_change_key
        :trype: str

        """
        self.new_email = email_new
        self.email_change_key = str(uuid.uuid4())
        return self.email_change_key

    def change_email(self):
        """
        Change email after activation.

        We don't clear new email field because of validator of email which won't allow to None value.

        """
        self.email = self.new_email
        self.email_change_key = None

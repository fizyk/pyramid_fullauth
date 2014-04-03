# Copyright (c) 2013 - 2014 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Email mixin related module."""

import re
import uuid

from sqlalchemy import Column
from sqlalchemy import Unicode
from sqlalchemy import String
from sqlalchemy.orm import validates


from pyramid_fullauth.exceptions import EmptyError, EmailValidationError

pattern_mail = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]{0,256}(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+){0,256}"  # dot-atom
    # quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177 ]|\\[\001-\011\013\014\016-\177 ]){0,256}"'
    r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2}\.?)$)'  # domain
    r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE)  # literal form, ipv4 address (SMTP 4.1.3)


class UserEmailMixin(object):

    """User email fields and functionality."""

    __pattern_mail = pattern_mail

    email = Column(Unicode(254), unique=True, nullable=False)  # RFC5321 and RFC3696(errata)
    new_email = Column(Unicode(254), unique=True, nullable=True)  # RFC5321 and RFC3696(errata)
    email_change_key = Column(String(255), default=None, unique=True)

    @validates('email', 'new_email')
    def validate_email(self, key, address):
        """
        Validate email addresses.

        .. note::

            See pyramid docs about `simple validators <http://docs.sqlalchemy.org/en/latest/orm/mapper_config.html#simple-validators>`_

        :param str key: field key
        :param str address: email address

        :raises EmailValidationError:
        :raises EmptyError:
        """
        if address:
            if pattern_mail.match(address):
                return address
            else:
                raise EmailValidationError('Incorrect e-mail format')

        raise EmptyError('E-mail is empty')

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

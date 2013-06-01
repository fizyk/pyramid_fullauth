# -*- coding: utf-8 -*-

import string
from random import choice


def password_generator(length, chars=(string.letters + string.digits + string.punctuation)):
    '''
        Generates random password

        .. warning::

            TODO: tests!

        :param int length: length of a password to Generates
        :param list chars: list of characters from which to choose
    '''
    return u''.join([choice(chars) for i in range(length)])

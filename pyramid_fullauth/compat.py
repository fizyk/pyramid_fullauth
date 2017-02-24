
# Copyright (c) 2013 - 2015 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""pyramid_fullauth's compatibility file for python2 and 3."""

import sys


if sys.version_info.major == 2:
    from urllib import urlencode
    from urlparse import urlparse, parse_qs
    from hashlib import algorithms
else:
    from urllib.parse import urlencode, urlparse, parse_qs
    from hashlib import algorithms_guaranteed as algorithms


__all__ = ('urlencode', 'urlparse', 'parse_qs', 'algorithms')

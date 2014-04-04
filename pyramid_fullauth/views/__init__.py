# Copyright (c) 2013 - 2014 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Views submodule."""


class BaseView(object):

    """basic view class."""

    def __init__(self, request):
        """Common init for views."""
        self.request = request
        self.config = request.registry['config'].fullauth

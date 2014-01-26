# -*- coding: utf-8 -*-

# Copyright (c) 2013 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT


class BaseView(object):

    '''basic view class'''

    def __init__(self, request):
        '''common init for views'''
        self.request = request
        self.config = request.registry['config'].fullauth

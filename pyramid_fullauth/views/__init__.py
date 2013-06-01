# -*- coding: utf-8 -*-


class BaseView(object):

    '''basic view class'''

    def __init__(self, request):
        '''common init for views'''
        self.request = request
        self.check_csrf = request.config.fullauth.check_csrf

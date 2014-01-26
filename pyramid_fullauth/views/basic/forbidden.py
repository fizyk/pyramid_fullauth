# -*- coding: utf-8 -*-

# Copyright (c) 2013 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT

from pyramid.view import forbidden_view_config
from pyramid.view import view_defaults
from pyramid.security import authenticated_userid
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.httpexceptions import HTTPFound

from pyramid_fullauth.views import BaseView


class ForbiddenViews(BaseView):

    @forbidden_view_config(renderer='pyramid_fullauth:resources/templates/403.mako')
    def forbidden(self):
        '''
            Forbidden page view.
        '''

        # do not allow a user to login if they are already logged in
        if authenticated_userid(self.request):
            self.request.response.status = '403 Forbidden'
            return {}

        loc = self.request.route_path('login', _query=(('after', self.request.path),))
        return HTTPFound(location=loc)

    @forbidden_view_config(xhr=True, renderer='json')
    def forbidden_json(self):
        '''
            Forbidden page view.
        '''

        self.request.response.status = '403 Forbidden'
        # do not allow a user to login if they are already logged in
        if authenticated_userid(self.request):
            return {'status': False, 'msg':
                    self.request._('forbidden-notallowed',
                                   default='You are not allowed to use this function',
                                   domain='pyramid_fullauth')}

        return {'status': False,
                'msg': self.request._('forbidden-login',
                                      default='You have to be logged in to use this function'),
                'login_url': self.request.route_path('login')}

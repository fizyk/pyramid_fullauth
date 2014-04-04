# -*- coding: utf-8 -*-

# Copyright (c) 2013 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.security import forget
from pyramid.security import NO_PERMISSION_REQUIRED

from sqlalchemy.orm.exc import NoResultFound
import pyramid_basemodel

from pyramid_fullauth.views import BaseView
from pyramid_fullauth.models import User
from pyramid_fullauth.events import BeforeLogIn
from pyramid_fullauth.events import AfterLogIn
from pyramid_fullauth.events import AlreadyLoggedIn


@view_defaults(permission=NO_PERMISSION_REQUIRED)
class LoginViews(BaseView):

    @view_config(route_name='login', request_method='GET',
                 renderer='pyramid_fullauth:resources/templates/login.mako')
    def login(self):
        """Display login page."""
        response = self._login_base_response()

        if authenticated_userid(self.request):
            return self._redirect_authenticated_user(response)

        self.request.registry.notify(BeforeLogIn(self.request, None))

        response['status'] = True
        del response['msg']
        return response

    @view_config(route_name='login', request_method='POST', check_csrf=True,
                 renderer='pyramid_fullauth:resources/templates/login.mako')
    @view_config(route_name='login', request_method='POST', check_csrf=True,
                 xhr=True, renderer="json")
    def login_POST(self):
        """Login action."""
        response = self._login_base_response()

        if authenticated_userid(self.request):
            return self._redirect_authenticated_user(response)

        email = self.request.POST.get('email', '')
        password = self.request.POST.get('password', '')
        try:
            user = pyramid_basemodel.Session.query(User).filter(User.email == email).one()
            try:
                self.request.registry.notify(BeforeLogIn(self.request, user))
            except AttributeError as e:
                response['msg'] = str(e)
                return response

            if user.check_password(password):
                try:
                    # if remember in POST set cookie timeout to one month
                    remember_me = self.request.POST.get('remember')
                    self.request.registry.notify(AfterLogIn(self.request, user))
                except HTTPFound as redirect:
                    redirect_return = self.request.login_perform(
                        user, location=redirect.location, remember_me=remember_me)
                    if self.request.is_xhr:
                        response['status'] = True
                        del response['msg']
                        response['after'] = redirect_return.location
                        return response
                    else:
                        return redirect_return
                except AttributeError as e:
                    response['msg'] = str(e)
                    return response
                else:
                    redirect = self.request.login_perform(user, remember_me=remember_me)
                    if self.request.is_xhr:
                        response['status'] = True
                        del response['msg']
                        response['after'] = redirect.location
                        return response
                    else:
                        return redirect
            else:
                response['msg'] = self.request._('Wrong e-mail or password.',
                                                 domain='pyramid_fullauth')
                return response
        except NoResultFound:
            self.request.registry.notify(BeforeLogIn(self.request, None))

            response['msg'] = self.request._('Wrong e-mail or password.',
                                             domain='pyramid_fullauth')
            return response

        response['status'] = True
        del response['msg']
        return response

    def _login_base_response(self):
        """
        Construct base response for login view.

        :returns: default login response
        :rtype: dict

        """
        return {
            'status': False,
            'msg': self.request._('Login error', domain='pyramid_fullauth'),
            'after': self.request.params.get(
                'after', self.request.referer or '/'),
            'csrf_token': self.request.session.get_csrf_token()
        }

    def _redirect_authenticated_user(self, response):
        """
        Redirect already logged in user away from login page.

        :param dict response: response dictionary

        """
        redirect = HTTPFound(location=response['after'])
        try:
            self.request.registry.notify(AlreadyLoggedIn(self.request))
        except HTTPFound as redirect:
            pass

        if self.request.is_xhr:
            response['status'] = True
            del response['msg']
            response['after'] = redirect.location
            return response
        else:
            return redirect

    @view_config(route_name='logout')
    def logout(self):
        '''
            Logout method
        '''
        location = '/'
        if self.config.redirects.logout:
            location = self.request.route_path(self.config.redirects.logout)

        return HTTPFound(location=location, headers=forget(self.request))

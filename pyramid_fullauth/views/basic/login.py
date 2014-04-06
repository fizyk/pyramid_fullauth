# Copyright (c) 2013 - 2014 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Authorisation related views."""

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.security import NO_PERMISSION_REQUIRED

from sqlalchemy.orm.exc import NoResultFound
import pyramid_basemodel

from pyramid_fullauth.views import BaseView
from pyramid_fullauth.models import User
from pyramid_fullauth.events import BeforeLogIn
from pyramid_fullauth.events import AfterLogIn
from pyramid_fullauth.events import AlreadyLoggedIn


@view_defaults(route_name='login', permission=NO_PERMISSION_REQUIRED,
               renderer='pyramid_fullauth:resources/templates/login.mako')
class BaseLoginView(BaseView):

    """Basic logic for login views."""

    def __init__(self, request):
        """Prepare login views."""
        super(BaseLoginView, self).__init__(request)

        self.response = {
            'status': False,
            'msg': self.request._('Login error', domain='pyramid_fullauth'),
            'after': self.request.params.get(
                'after', self.request.referer or '/'),
            'csrf_token': self.request.session.get_csrf_token()
        }

    def _redirect_authenticated_user(self):
        """Redirect already logged in user away from login page."""
        redirect = HTTPFound(location=self.response['after'])
        try:
            self.request.registry.notify(AlreadyLoggedIn(self.request))
        except HTTPFound as redirect:
            pass

        if self.request.is_xhr:
            self.response['status'] = True
            del self.response['msg']
            self.response['after'] = redirect.location
            return self.response
        else:
            return redirect


@view_config(request_method='GET')
class LoginView(BaseLoginView):

    """Login view."""

    def __call__(self):
        """Display login page."""
        if authenticated_userid(self.request):
            return self._redirect_authenticated_user()

        self.request.registry.notify(BeforeLogIn(self.request, None))

        self.response['status'] = True
        del self.response['msg']
        return self.response


@view_config(request_method='POST', check_csrf=True)
@view_config(request_method='POST', check_csrf=True, xhr=True, renderer="json")
class LoginViewPost(BaseLoginView):

    """Login view POST method."""

    def __call__(self):
        """Login action."""
        if authenticated_userid(self.request):
            return self._redirect_authenticated_user()

        email = self.request.POST.get('email', '')
        password = self.request.POST.get('password', '')
        try:
            user = pyramid_basemodel.Session.query(User).filter(User.email == email).one()
            try:
                self.request.registry.notify(BeforeLogIn(self.request, user))
            except AttributeError as e:
                self.response['msg'] = str(e)
                return self.response

            if user.check_password(password):
                try:
                    # if remember in POST set cookie timeout to one month
                    remember_me = self.request.POST.get('remember')
                    self.request.registry.notify(AfterLogIn(self.request, user))
                except HTTPFound as redirect:
                    redirect_return = self.request.login_perform(
                        user, location=redirect.location, remember_me=remember_me)
                    if self.request.is_xhr:
                        self.response['status'] = True
                        del self.response['msg']
                        self.response['after'] = redirect_return.location
                        return self.response
                    else:
                        return redirect_return
                except AttributeError as e:
                    self.response['msg'] = str(e)
                    return self.response
                else:
                    redirect = self.request.login_perform(user, remember_me=remember_me)
                    if self.request.is_xhr:
                        self.response['status'] = True
                        del self.response['msg']
                        self.response['after'] = redirect.location
                        return self.response
                    else:
                        return redirect
            else:
                self.response['msg'] = self.request._('Wrong e-mail or password.',
                                                      domain='pyramid_fullauth')
                return self.response
        except NoResultFound:
            self.request.registry.notify(BeforeLogIn(self.request, None))

            self.response['msg'] = self.request._('Wrong e-mail or password.',
                                                  domain='pyramid_fullauth')
            return self.response

        self.response['status'] = True
        del self.response['msg']
        return self.response

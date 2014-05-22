# Copyright (c) 2013 - 2014 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Registration related views."""

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPRedirection
from pyramid.security import NO_PERMISSION_REQUIRED

import pyramid_basemodel

from pyramid_fullauth.views import BaseView
from pyramid_fullauth.models import User, AuthenticationProvider
from pyramid_fullauth.events import BeforeRegister, AfterRegister
from pyramid_fullauth import tools
from pyramid_fullauth.exceptions import ValidateError


@view_defaults(route_name='register', permission=NO_PERMISSION_REQUIRED,
               renderer="pyramid_fullauth:resources/templates/register.mako")
class RegisterView(BaseView):

    """Registration views."""

    @view_config(request_method='GET')
    def get(self):
        """Display registration form."""
        csrf_token = self.request.session.get_csrf_token()
        return {'status': True, 'msg': None, 'csrf_token': csrf_token, 'errors': {}}

    @view_config(request_method='POST', check_csrf=True)
    @view_config(request_method='POST', check_csrf=True, xhr=True, renderer="json")
    def post(self):
        """Process registration request."""
        response = {
            'status': False,
            'msg': self.request._('You have an error in your registration form',
                                  domain='pyramid_fullauth'),
            'csrf_token': self.request.session.get_csrf_token(),
            'errors': {},
        }

        user = User()
        user.address_ip = self.request.remote_addr

        response = self._fillin_user(response, user)

        if not response['errors']:
            response['status'] = True
            response['msg'] = self.request._(
                'You have successfully registered', domain='pyramid_fullauth')

        try:
            self.request.registry.notify(AfterRegister(self.request, user, response))
        except HTTPRedirection as redirect:
            return redirect

        return response

    def _fillin_user(self, response, user):
        """
        Fill new user object in, with sent data.

        :param dict response: response to return from register view
        :param pyramid_fullauth.models.User user: new user object

        :returns: response
        :rtype: dict
        """
        email = self.request.POST.get('email', u'')
        # here if e-mail is already in database

        if pyramid_basemodel.Session.query(User).filter(User.email == email).count() != 0:
            response['errors']['email'] = self.request._(
                'User with given e-mail already exists!',
                domain='pyramid_fullauth')
        try:
            try:
                user.email = email
            except ValidateError as e:
                # do not overwrite existing error
                if 'email' not in response['errors']:
                    response['errors']['email'] = str(e)

            if self.config.register.password.require:
                try:
                    tools.validate_passsword(self.request,
                                             self.request.POST.get('password', u''),
                                             user)
                except ValidateError as e:
                    response['errors']['password'] = e.message
            else:
                user.password = tools.password_generator(
                    self.config.register.password.length_min)

            self.request.registry.notify(BeforeRegister(self.request, user, response['errors']))
            if not response['errors']:
                pyramid_basemodel.Session.add(user)
                pyramid_basemodel.Session.flush()

                # lets add AuthenticationProvider as email!
                user.providers.append(
                    AuthenticationProvider(provider=u'email', provider_id=user.id))
            else:
                return response
        except AttributeError as e:
            response['errors']['msg'] = str(e)

        return response

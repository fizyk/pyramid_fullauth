# -*- coding: utf-8 -*-

# Copyright (c) 2013 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT

from pyramid.view import view_config
from pyramid.view import forbidden_view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound

from pyramid.security import authenticated_userid
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.compat import text_type

from sqlalchemy.orm.exc import NoResultFound

from pyramid_basemodel import Session
from pyramid_fullauth.views import BaseView
from pyramid_fullauth.models import User
from pyramid_fullauth.models import AuthenticationProvider
from pyramid_fullauth.events import BeforeRegister
from pyramid_fullauth.events import AfterRegister
from pyramid_fullauth.events import AfterActivate
from pyramid_fullauth.events import AfterResetRequest
from pyramid_fullauth.events import BeforeReset
from pyramid_fullauth.events import AfterReset
from pyramid_fullauth import tools
from pyramid_fullauth.auth import force_logout
from pyramid_fullauth.exceptions import ValidateError


@view_defaults(permission=NO_PERMISSION_REQUIRED)
class RegisterViews(BaseView):

    @view_config(route_name='register:activate',
                 renderer="pyramid_fullauth:resources/templates/activate.mako")
    def activate(self):
        '''
            Process account activation
        '''

        activate_hash = self.request.matchdict.get('hash')
        user = None
        response = {}
        response['status'] = True
        if activate_hash:
            try:
                user = Session.query(User).filter(User.activate_key == activate_hash).one()
                if not user.is_active:
                    user.is_active = True
            except NoResultFound:
                response['status'] = False
        try:
            self.request.registry.notify(AfterActivate(self.request, user))
        except HTTPFound as e:
            # it's a redirect, let's follow it!
            return e

        return response

    @view_config(route_name='register',
                 renderer="pyramid_fullauth:resources/templates/register.mako")
    def register(self):
        '''
            Processes register
        '''

        csrf_token = self.request.session.get_csrf_token()
        return {'status': True, 'msg': None, 'csrf_token': csrf_token, 'errors': {}}

    @view_config(route_name='register', request_method='POST',
                 renderer="pyramid_fullauth:resources/templates/register.mako",
                 check_csrf=True)
    @view_config(route_name='register', request_method='POST', xhr=True,
                 check_csrf=True, renderer="json")
    def register_POST(self):
        '''
            Process POST register request
        '''

        invalid_fields = {}
        response_values = {
            'status': False,
            'msg': self.request._('You have an error in your registration form',
                                  domain='pyramid_fullauth'),
            'csrf_token': self.request.session.get_csrf_token()}
        response_values['errors'] = invalid_fields

        email = self.request.POST.get('email', u'')
        # here if e-mail is already in database
        try:
            Session.query(User).filter(User.email == email).one()
            invalid_fields['email'] = self.request._('User with given e-mail already exists!',
                                                     domain='pyramid_fullauth')
        except NoResultFound:
            pass

        try:
            user = User()
            try:
                user.email = email
            except ValidateError as e:
                # do not overwrite existing error
                if not 'email' in invalid_fields:
                    invalid_fields['email'] = str(e)

            user.address_ip = self.request.remote_addr

            if self.request.registry['config'].fullauth.register.password.require:
                try:
                    tools.validate_passsword(self.request,
                                             self.request.POST.get('password', u''),
                                             user)
                except ValidateError as e:
                    invalid_fields['password'] = e.message
            else:
                user.password = tools.password_generator(
                    self.request.registry['config'].fullauth.register.password.length_min)

            self.request.registry.notify(BeforeRegister(self.request, user, invalid_fields))
            if not invalid_fields:
                Session.add(user)
                Session.flush()
                # lets add AuthenticationProvider as email!
                user.providers.append(
                    AuthenticationProvider(provider=u'email', provider_id=user.id))
            else:
                return response_values
        except AttributeError as e:
            invalid_fields['msg'] = str(e)
            return response_values

        response_values['status'] = True
        response_values['msg'] = self.request._('You have successfully registered',
                                                domain='pyramid_fullauth')

        try:
            self.request.registry.notify(AfterRegister(self.request, user, response_values))
        except HTTPFound as redirect:
            return redirect

        return response_values

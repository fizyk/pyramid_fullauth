# -*- coding: utf-8 -*-

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


@view_defaults(permission=NO_PERMISSION_REQUIRED)
class RegisterViews(BaseView):

    @view_config(route_name='register:activate',
                 renderer="pyramid_fullauth:resources/templates/activate.mako")
    def activate(self):
        '''
            Process account activation
        '''
        user = self.request.matchdict.get('user')
        # let's clear activation_key
        user.is_active = True

        try:
            self.request.registry.notify(AfterActivate(self.request, user))
        except HTTPFound as e:
            # it's a redirect, let's follow it!
            return e
        return {}

    @view_config(route_name='register',
                 renderer="pyramid_fullauth:resources/templates/register.mako")
    def register(self):
        '''
            Processes register
        '''

        if self.check_csrf:
            token = self.request.session.get_csrf_token()
        else:
            token = ''
        return {'status': True, 'msg': None, 'token': token, 'errors': {}}

    @view_config(route_name='register', request_method='POST',
                 renderer="pyramid_fullauth:resources/templates/register.mako")
    @view_config(route_name='register', request_method='POST', xhr=True,
                 renderer="json")
    def register_POST(self):
        '''
            Process POST register request
        '''

        invalid_fields = {}
        response_values = {
            'status': False,
            'msg': self.request._('csrf-mismatch',
                                  default='CSRF token did not match.',
                                  domain='pyramid_fullauth'),
            'token': ''}
        response_values['errors'] = invalid_fields
        if self.check_csrf:
            token = self.request.session.get_csrf_token()
        else:
            token = ''

        response_values['token'] = token
        if self.check_csrf and token != self.request.POST.get('token'):
            invalid_fields['token'] = self.request._('csrf-mismatch',
                                                     default='CSRF token did not match.',
                                                     domain='pyramid_fullauth'),

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
            except AttributeError as e:
                # do not overwrite existing error
                if not 'email' in invalid_fields:
                    invalid_fields['email'] = str(e)

            user.address_ip = self.request.remote_addr

            if self.request.config.fullauth.register.password.require:
                password = self.request.POST.get('password', u'')
                passwordMinLen = self.request.config.fullauth.register.password.length_min
                password_confirm = self.request.POST.get('password_confirm', u'')
                if not password:
                    invalid_fields['password'] = self.request._('Please enter your password',
                                                                domain='pyramid_fullauth')
                elif passwordMinLen > 0 and len(password) < passwordMinLen:
                    invalid_fields['password'] = self.request._('Password is too short',
                                                                domain='pyramid_fullauth')

                # here if password doesn't match
                password_options = self.request.config.fullauth.register.password
                if password_options['confirm']:
                    password_confirm = self.request.POST.get('password_confirm', u'')
                    if password != password_confirm:
                        invalid_fields['password_confirm'] = self.request._(
                            'Passwords don\'t match',
                            domain='pyramid_fullauth')

            else:
                password = tools.password_generator(getattr(
                    self.request.config.fullauth.register.password, 'length_min', 8))

            if password:
                user.password = password
            else:
                if not 'password' in invalid_fields:
                    invalid_fields['password'] = self.request._('Please enter your password',
                                                                domain='pyramid_fullauth')

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

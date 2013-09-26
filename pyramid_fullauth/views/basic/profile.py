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

from pyramid_basemodel import Session

from pyramid_fullauth.views import BaseView
from pyramid_fullauth.auth import force_logout
from pyramid_fullauth.models import User, AuthenticationProvider

from pyramid_fullauth.events import BeforeEmailChange
from pyramid_fullauth.events import AfterEmailChange
from pyramid_fullauth.events import AfterEmailChangeActivation
from pyramid_fullauth.events import BeforeReset
from pyramid_fullauth.events import AfterResetRequest
from pyramid_fullauth.events import AfterReset
from pyramid_fullauth.exceptions import (
    ValidateError, EmptyError, EmailValidationError
)
from pyramid_fullauth.tools import validate_passsword


@view_defaults(permission=NO_PERMISSION_REQUIRED)
class ProfileViews(BaseView):

    @view_config(route_name='email:change', permission='email_change',
                 renderer='pyramid_fullauth:resources/templates/email_change.mako')
    def email_change(self):
        return {'status': True, 'csrf_token': self.request.session.get_csrf_token()}

    @view_config(route_name='email:change', permission='email_change',
                 request_method='POST', check_csrf='csrf_token',
                 renderer='pyramid_fullauth:resources/templates/email_change.mako')
    @view_config(route_name='email:change', permission='email_change',
                 request_method='POST', check_csrf='csrf_token',
                 xhr=True, renderer="json")
    def email_change_POST(self):
        '''
            Processes POST requests to generate change email hash
        '''
        csrf_token = self.request.session.get_csrf_token()
        try:
            Session.query(User).filter(User.email == self.request.POST.get('email', '')).one()
            return {'status': False,
                    'msg': self.request._('User with this email exists',
                                          domain='pyramid_fullauth'),
                    'csrf_token': csrf_token}
        except NoResultFound:
            pass

        user = self.request.user
        try:
            result = self.request.registry.notify(BeforeEmailChange(self.request, user))
        except AttributeError as e:
            return {'status': False, 'msg': e.message, 'csrf_token': csrf_token}

        try:
            user.set_new_email(self.request.POST.get('email', ''))
        except EmptyError:
            return {'status': False,
                    'msg': self.request._(
                        'E-mail is empty',
                        domain='pyramid_fullauth'),
                    'csrf_token': csrf_token}
        except EmailValidationError:
            return {'status': False,
                    'msg': self.request._(
                        'Incorrect e-mail format',
                        domain='pyramid_fullauth'),
                    'csrf_token': csrf_token}

        response_values = {
            'status': True,
            'msg': self.request._('We sent you email to activate your new email address',
                                  domain='pyramid_fullauth')
        }

        try:
            self.request.registry.notify(AfterEmailChange(self.request, user))
        except HTTPFound as redirect:
            if self.request.is_xhr:
                response_values['url'] = redirect.location
                return response_values
            else:
                return redirect
        else:
            if self.request.is_xhr:
                return response_values
            else:
                return HTTPFound(location='/')

    @view_config(route_name='email:change:continue',
                 renderer='pyramid_fullauth:resources/templates/email_change.mako')
    def email_change_continue(self):
        '''
            Method that changes email address to new one after email activation
        '''
        user = self.request.matchdict.get('user')
        user.change_email()

        try:
            self.request.registry.notify(AfterEmailChangeActivation(self.request, user))
        except HTTPFound as redirect:
            return redirect
        return HTTPFound(location='/')

    @view_config(route_name='password:reset',
                 renderer='pyramid_fullauth:resources/templates/reset.mako')
    def reset(self):
        '''
            Password reset method
        '''
        csrf_token = self.request.session.get_csrf_token()

        return {'status': True, 'csrf_token': csrf_token}

    @view_config(route_name='password:reset', request_method='POST',
                 check_csrf=True,
                 renderer='pyramid_fullauth:resources/templates/reset.mako')
    def reset_POST(self):
        '''
            Processes POST requests to generate reset password hashes
        '''
        csrf_token = self.request.session.get_csrf_token()

        try:
            user = Session.query(User).filter(
                User.email == self.request.POST.get('email', '')).one()
        except NoResultFound:
            return {'status': False,
                    'msg': self.request._('user-not-exists',
                                          default='User does not exists',
                                          domain='pyramid_fullauth'),
                    'csrf_token': csrf_token}

        user.set_reset()
        try:
            self.request.registry.notify(AfterResetRequest(self.request, user))
        except HTTPFound as redirect:
            return redirect

        return HTTPFound(location='/')

    @force_logout()
    @view_config(route_name='password:reset:continue', request_method='GET',
                 renderer='pyramid_fullauth:resources/templates/reset.proceed.mako')
    @view_config(route_name='password:reset:continue',
                 request_method='POST', check_csrf=True,
                 renderer='pyramid_fullauth:resources/templates/reset.proceed.mako')
    def reset_continue(self):
        '''
            Method that serves password reset page
        '''
        user = self.request.matchdict.get('user')

        csrf_token = self.request.session.get_csrf_token()

        if self.request.method == 'POST':

            password = self.request.POST.get('password', None)
            password_confirm = self.request.POST.get('confirm_password', None)
            if password == password_confirm:

                try:
                    self.request.registry.notify(BeforeReset(self.request, user))
                    validate_passsword(self.request, password, user)

                    user.reset_key = None
                    try:
                        Session.query(AuthenticationProvider).filter(
                            AuthenticationProvider.user_id == user.id,
                            AuthenticationProvider.provider == u'email').one()
                    except NoResultFound:
                        user.providers.append(
                            AuthenticationProvider(provider=u'email',
                                                   provider_id=user.id))

                    Session.flush()
                except (ValidateError, AttributeError) as e:
                    return {'status': False, 'msg': str(e), 'csrf_token': csrf_token}

                try:
                    self.request.registry.notify(AfterReset(self.request, user))
                except HTTPFound as redirect:
                    return redirect
            else:
                return {'status': False,
                        'msg': self.request._('password-mismatch',
                                              default='Password doesn\'t match',
                                              domain='pyramid_fullauth'),
                        'csrf_token': csrf_token}

        return {'status': True, 'csrf_token': csrf_token}

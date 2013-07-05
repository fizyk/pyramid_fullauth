# -*- coding: utf-8 -*-

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
from pyramid_fullauth.models import User
from pyramid_fullauth.models import AuthenticationProvider

from pyramid_fullauth.events import BeforeEmailChange
from pyramid_fullauth.events import AfterEmailChange
from pyramid_fullauth.events import AfterEmailChangeActivation
from pyramid_fullauth.events import BeforeReset
from pyramid_fullauth.events import AfterResetRequest
from pyramid_fullauth.events import AfterReset


@view_defaults(permission=NO_PERMISSION_REQUIRED)
class ProfileViews(BaseView):

    @view_config(route_name='email:change', permission='email_change', renderer='pyramid_fullauth:resources/templates/email_change.mako')
    def email_change(self):
        if self.check_csrf:
            token = self.request.session.get_csrf_token()
        else:
            token = ''
        return {'status': True, 'token': token}

    @view_config(route_name='email:change', permission='email_change', request_method='POST',
                 renderer='pyramid_fullauth:resources/templates/email_change.mako')
    @view_config(route_name='email:change', permission='email_change', request_method='POST', xhr=True, renderer="json")
    def email_change_POST(self):
        '''
            Processes POST requests to generate change email hash
        '''
        if self.check_csrf:
            token = self.request.session.get_csrf_token()
        else:
            token = ''
        if self.check_csrf and token != self.request.POST.get('token'):
            return {'status': False,
                    'msg': self.request._('csrf-mismatch',
                                          default='CSRF token did not match.',
                                          domain='pyramid_fullauth'),
                    'token': token}
        try:
            Session.query(User).filter(User.email == self.request.POST.get('email', '')).one()
            return {'status': False,
                    'msg': self.request._('User with this email exists',
                                          domain='pyramid_fullauth'),
                    'token': token}
        except NoResultFound:
            pass

        user = self.request.user
        try:
            result = self.request.registry.notify(BeforeEmailChange(self.request, user))
        except AttributeError as e:
            return {'status': False, 'msg': e.message, 'token': token}

        try:
            user.set_new_email(self.request.POST.get('email', ''))
        except AttributeError as e:
            return {'status': False, 'msg': e.message, 'token': token}

        response_values = {'status': True,
                           'msg': self.request._('We sent you email to activate your new email address',
                                                 domain='pyramid_fullauth')}
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

    @view_config(route_name='email:change:continue', renderer='pyramid_fullauth:resources/templates/email_change.mako')
    def email_change_continue(self):
        '''
            Method that changes email address to new one after email activation
        '''
        user = self.request.matchdict.get('user')
        if self.check_csrf:
            token = self.request.session.get_csrf_token()
        else:
            token = ''

        user.change_email()

        try:
            self.request.registry.notify(AfterEmailChangeActivation(self.request, user))
        except HTTPFound as redirect:
            return redirect
        return HTTPFound(location='/')

    @view_config(route_name='password:reset', renderer='pyramid_fullauth:resources/templates/reset.mako')
    def reset(self):
        '''
            Password reset method
        '''
        if self.check_csrf:
            token = self.request.session.get_csrf_token()
        else:
            token = ''

        return {'status': True, 'token': token}

    @view_config(route_name='password:reset', request_method='POST', renderer='pyramid_fullauth:resources/templates/reset.mako')
    def reset_POST(self):
        '''
            Processes POST requests to generate reset password hashes
        '''
        if self.check_csrf:
            token = self.request.session.get_csrf_token()
        else:
            token = ''
        if self.check_csrf and token != self.request.POST.get('token'):
            return {'status': False,
                    'msg': self.request._('csrf-mismatch',
                                          default='CSRF token did not match.',
                                          domain='pyramid_fullauth'),
                    'token': token}
        try:
            user = Session.query(User).filter(User.email == self.request.POST.get('email', '')).one()
        except NoResultFound:
            return {'status': False,
                    'msg': self.request._('user-not-exists',
                                          default='User does not exists',
                                          domain='pyramid_fullauth'),
                    'token': token}

        user.set_reset()
        try:
            self.request.registry.notify(AfterResetRequest(self.request, user))
        except HTTPFound as redirect:
            return redirect

        return HTTPFound(location='/')

    @force_logout()
    @view_config(route_name='password:reset:continue', renderer='pyramid_fullauth:resources/templates/reset.proceed.mako')
    def reset_continue(self):
        '''
            Method that serves password reset page
        '''
        user = self.request.matchdict.get('user')
        if self.check_csrf:
            token = self.request.session.get_csrf_token()
        else:
            token = ''

        if self.request.method == 'POST':
            # if turned on, check for csrf token
            if self.check_csrf and token != self.request.POST.get('token'):
                return {'status': False,
                        'msg': self.request._('csrf-mismatch',
                                              default='CSRF token did not match.',
                                              domain='pyramid_fullauth'),
                        'token': token}

            password = self.request.POST.get('password', None)
            password_confirm = self.request.POST.get('confirm_password', None)
            if password and password == password_confirm:
                user.password = password

                try:
                    self.request.registry.notify(BeforeReset(self.request, user))
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
                except AttributeError as e:
                    return {'status': False, 'msg': str(e), 'token': token}

                try:
                    self.request.registry.notify(AfterReset(self.request, user))
                except HTTPFound as redirect:
                    return redirect
            else:
                return {'status': False,
                        'msg': self.request._('password-mismatch',
                                              default='Password doesn\'t match',
                                              domain='pyramid_fullauth'),
                        'token': token}

        return {'status': True, 'token': token}

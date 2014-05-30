# Copyright (c) 2013 - 2014 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Email related views."""

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPRedirection, HTTPSeeOther
from pyramid.security import NO_PERMISSION_REQUIRED

from sqlalchemy.orm.exc import NoResultFound
from pyramid.compat import text_type
import pyramid_basemodel

from pyramid_fullauth.views import BaseView
from pyramid_fullauth.models import User

from pyramid_fullauth.events import BeforeEmailChange
from pyramid_fullauth.events import AfterEmailChange
from pyramid_fullauth.events import AfterEmailChangeActivation
from pyramid_fullauth.exceptions import EmptyError, EmailValidationError


@view_defaults(route_name='email:change', permission='email_change',
               renderer='pyramid_fullauth:resources/templates/email_change.mako')
class EmailChangeViews(BaseView):

    """Email change related views."""

    @view_config(request_method='GET')
    def get(self):
        """Display email change request form."""
        return {'status': True, 'csrf_token': self.request.session.get_csrf_token()}

    @view_config(request_method='POST', check_csrf='csrf_token')
    @view_config(request_method='POST', check_csrf='csrf_token', xhr=True, renderer="json")
    def post(self):
        """Process email change request."""
        csrf_token = self.request.session.get_csrf_token()
        try:
            pyramid_basemodel.Session.query(User).filter(
                User.email == self.request.POST.get('email', '')
            ).one()
            return {'status': False,
                    'msg': self.request._('User with this email exists',
                                          domain='pyramid_fullauth'),
                    'csrf_token': csrf_token}
        except NoResultFound:
            pass

        user = self.request.user
        try:
            self.request.registry.notify(BeforeEmailChange(self.request, user))
        except AttributeError as e:
            return {'status': False, 'msg': text_type(e), 'csrf_token': csrf_token}

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
        except HTTPRedirection as redirect:
            if self.request.is_xhr:
                response_values['url'] = redirect.location
                return response_values
            else:
                return redirect
        else:
            if self.request.is_xhr:
                return response_values
            else:
                return HTTPSeeOther(location='/')


@view_config(route_name='email:change:continue', permission=NO_PERMISSION_REQUIRED,
             renderer='pyramid_fullauth:resources/templates/email_change.mako')
class EmailChangeAccept(BaseView):

    """Display email change success."""

    def __call__(self):
        """View that changes user email."""
        user = self.request.matchdict.get('user')
        user.change_email()

        try:
            self.request.registry.notify(AfterEmailChangeActivation(self.request, user))
        except HTTPRedirection as redirect:
            return redirect
        return HTTPSeeOther(location='/')

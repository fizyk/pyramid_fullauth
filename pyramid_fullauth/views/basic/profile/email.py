# Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Email related views."""

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPRedirection, HTTPSeeOther
from pyramid.security import NO_PERMISSION_REQUIRED

import pyramid_basemodel

from pyramid_fullauth.views import BaseView
from pyramid_fullauth.models import User

from pyramid_fullauth.events import BeforeEmailChange
from pyramid_fullauth.events import AfterEmailChange
from pyramid_fullauth.events import AfterEmailChangeActivation
from pyramid_fullauth.exceptions import EmptyError, EmailValidationError


@view_defaults(
    route_name="email:change",
    permission="email_change",
    renderer="pyramid_fullauth:resources/templates/email_change.mako",
)
class EmailChangeViews(BaseView):
    """Email change related views."""

    @view_config(request_method="GET")
    def get(self):
        """Display email change request form."""
        return {"status": True, "csrf_token": self.request.session.get_csrf_token()}

    @view_config(request_method="POST")
    @view_config(request_method="POST", xhr=True, renderer="json")
    def post(self):
        """Process email change request."""
        user = self.request.user
        response = self.validate_email(user)
        if response:
            return response

        response_values = {
            "status": True,
            "msg": self.request._(
                "We sent you email to activate your new email address",
                domain="pyramid_fullauth",
            ),
        }

        try:
            self.request.registry.notify(AfterEmailChange(self.request, user))
        except HTTPRedirection as redirect:
            if self.request.is_xhr:
                response_values["url"] = redirect.location
                return response_values
            return redirect
        else:
            if self.request.is_xhr:
                return response_values
            return HTTPSeeOther(location="/")

    def validate_email(self, user):
        """
        Validate and set email on a user object.

        :param pyramid_fullauth.models.User user: user to set an email passed on POST arguments.

        :returns: response in case of an invalid email, None otherwise
        :rtype: dict
        """
        csrf_token = self.request.session.get_csrf_token()
        email = self.request.POST.get("email", "")
        if pyramid_basemodel.Session.query(User).filter(User.email == email).first():
            return {
                "status": False,
                "msg": self.request._("User with this email exists", domain="pyramid_fullauth"),
                "csrf_token": csrf_token,
            }

        try:
            self.request.registry.notify(BeforeEmailChange(self.request, user))
        except AttributeError as ex:
            return {"status": False, "msg": str(ex), "csrf_token": csrf_token}

        try:
            user.set_new_email(email)
        except EmptyError:
            return {
                "status": False,
                "msg": self.request._("E-mail is empty", domain="pyramid_fullauth"),
                "csrf_token": csrf_token,
            }
        except EmailValidationError:
            return {
                "status": False,
                "msg": self.request._("Incorrect e-mail format", domain="pyramid_fullauth"),
                "csrf_token": csrf_token,
            }
        return None


@view_config(
    route_name="email:change:continue",
    permission=NO_PERMISSION_REQUIRED,
    renderer="pyramid_fullauth:resources/templates/email_change.mako",
)
class EmailChangeAccept(BaseView):
    """Display email change success."""

    def __call__(self):
        """View that changes user email."""
        user = self.request.matchdict.get("user")
        user.change_email()

        try:
            self.request.registry.notify(AfterEmailChangeActivation(self.request, user))
        except HTTPRedirection as redirect:
            return redirect
        return HTTPSeeOther(location="/")

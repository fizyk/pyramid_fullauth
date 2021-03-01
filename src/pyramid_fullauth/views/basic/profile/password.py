# Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Profile related views."""

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPRedirection, HTTPSeeOther
from pyramid.security import NO_PERMISSION_REQUIRED
from sqlalchemy.orm.exc import NoResultFound
import pyramid_basemodel

from pyramid_fullauth.views import BaseView
from pyramid_fullauth.models import User, AuthenticationProvider

from pyramid_fullauth.events import BeforeReset
from pyramid_fullauth.events import AfterResetRequest
from pyramid_fullauth.events import AfterReset
from pyramid_fullauth.exceptions import ValidateError
from pyramid_fullauth.tools import validate_passsword


@view_defaults(
    route_name="password:reset",
    permission=NO_PERMISSION_REQUIRED,
    renderer="pyramid_fullauth:resources/templates/reset.mako",
)
class PasswordResetView(BaseView):
    """Profile related views."""

    @view_config()
    def get(self):
        """Password reset request view."""
        csrf_token = self.request.session.get_csrf_token()

        return {"status": True, "csrf_token": csrf_token}

    @view_config(request_method="POST")
    def post(self):
        """View processing requests to reset password."""
        csrf_token = self.request.session.get_csrf_token()

        try:
            user = pyramid_basemodel.Session.query(User).filter(User.email == self.request.POST.get("email", "")).one()
        except NoResultFound:
            return {
                "status": False,
                "msg": self.request._(
                    "user-not-exists",
                    default="User does not exist",
                    domain="pyramid_fullauth",
                ),
                "csrf_token": csrf_token,
            }

        user.set_reset()
        try:
            self.request.registry.notify(AfterResetRequest(self.request, user))
        except HTTPRedirection as redirect:
            return redirect

        return HTTPSeeOther(location="/")


@view_defaults(
    route_name="password:reset:continue",
    permission=NO_PERMISSION_REQUIRED,
    renderer="pyramid_fullauth:resources/templates/reset.proceed.mako",
)
class PasswordResetContinueView(BaseView):
    """
    Password reset views.

    These views display actual reset password views.
    """

    @view_config(request_method="GET")
    def get(self):
        """Display actual password reset form."""
        self.request.logout()
        return {"status": True, "csrf_token": self.request.session.get_csrf_token()}

    @view_config(request_method="POST")
    def post(self):
        """Validate and possibly accept new email."""
        user = self.request.matchdict.get("user")

        password = self.request.POST.get("password", None)
        password_confirm = self.request.POST.get("confirm_password", None)
        if password == password_confirm:

            try:
                self.request.registry.notify(BeforeReset(self.request, user))
                validate_passsword(self.request, password, user)

                user.reset_key = None
                try:
                    pyramid_basemodel.Session.query(AuthenticationProvider).filter(
                        AuthenticationProvider.user_id == user.id,
                        AuthenticationProvider.provider == "email",
                    ).one()
                except NoResultFound:
                    user.providers.append(AuthenticationProvider(provider="email", provider_id=user.id))

                pyramid_basemodel.Session.flush()
            except (ValidateError, AttributeError) as ex:
                return {
                    "status": False,
                    "msg": str(ex),
                    "csrf_token": self.request.session.get_csrf_token(),
                }

            try:
                self.request.registry.notify(AfterReset(self.request, user))
            except HTTPRedirection as redirect:
                return redirect
        else:
            return {
                "status": False,
                "msg": self.request._(
                    "password-mismatch",
                    default="Password doesn't match",
                    domain="pyramid_fullauth",
                ),
                "csrf_token": self.request.session.get_csrf_token(),
            }

        return self.get()

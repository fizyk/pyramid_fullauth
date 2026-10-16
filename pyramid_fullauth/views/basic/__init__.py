# Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Basic views."""

from pyramid.config import Configurator
from pyramid.security import NO_PERMISSION_REQUIRED

from pyramid_fullauth.views.basic.activate import ActivateView
from pyramid_fullauth.views.basic.forbidden import ForbiddenViews
from pyramid_fullauth.views.basic.login import LoginView, LoginViewPost
from pyramid_fullauth.views.basic.logout import LogoutView
from pyramid_fullauth.views.basic.profile.email import EmailChangeAccept, EmailChangeViews
from pyramid_fullauth.views.basic.profile.password import PasswordResetContinueView, PasswordResetView
from pyramid_fullauth.views.basic.register import RegisterView


def includeme(configurator: Configurator) -> None:
    """Register basic fullauth views.

    :param pyramid.configurator.Configurator configurator: pyramid's configurator object
    """
    # login
    login = {
        "route_name": "login",
        "permission": NO_PERMISSION_REQUIRED,
        "renderer": "pyramid_fullauth:resources/templates/login.mako",
    }
    configurator.add_view(LoginView, request_method="GET", **login)
    configurator.add_view(LoginViewPost, request_method="POST", **login)
    configurator.add_view(LoginViewPost, request_method="POST", xhr=True, **{**login, "renderer": "json"})

    # logout
    configurator.add_view(LogoutView, route_name="logout", permission=NO_PERMISSION_REQUIRED)

    # register
    register = {
        "route_name": "register",
        "permission": NO_PERMISSION_REQUIRED,
        "renderer": "pyramid_fullauth:resources/templates/register.mako",
    }
    configurator.add_view(RegisterView, attr="get", request_method="GET", **register)
    configurator.add_view(RegisterView, attr="post", request_method="POST", **register)
    configurator.add_view(
        RegisterView, attr="post", request_method="POST", xhr=True, **{**register, "renderer": "json"}
    )

    # account activation
    configurator.add_view(
        ActivateView,
        route_name="register:activate",
        permission=NO_PERMISSION_REQUIRED,
        renderer="pyramid_fullauth:resources/templates/activate.mako",
    )

    # password reset
    password_reset = {
        "route_name": "password:reset",
        "permission": NO_PERMISSION_REQUIRED,
        "renderer": "pyramid_fullauth:resources/templates/reset.mako",
    }
    configurator.add_view(PasswordResetView, attr="get", **password_reset)
    configurator.add_view(PasswordResetView, attr="post", request_method="POST", **password_reset)

    password_reset_continue = {
        "route_name": "password:reset:continue",
        "permission": NO_PERMISSION_REQUIRED,
        "renderer": "pyramid_fullauth:resources/templates/reset.proceed.mako",
    }
    configurator.add_view(PasswordResetContinueView, attr="get", request_method="GET", **password_reset_continue)
    configurator.add_view(PasswordResetContinueView, attr="post", request_method="POST", **password_reset_continue)

    # email change
    email_change = {
        "route_name": "email:change",
        "permission": "email_change",
        "renderer": "pyramid_fullauth:resources/templates/email_change.mako",
    }
    configurator.add_view(EmailChangeViews, attr="get", request_method="GET", **email_change)
    configurator.add_view(EmailChangeViews, attr="post", request_method="POST", **email_change)
    configurator.add_view(
        EmailChangeViews, attr="post", request_method="POST", xhr=True, **{**email_change, "renderer": "json"}
    )
    configurator.add_view(
        EmailChangeAccept,
        route_name="email:change:continue",
        permission=NO_PERMISSION_REQUIRED,
        renderer="pyramid_fullauth:resources/templates/email_change.mako",
    )

    # forbidden
    configurator.add_forbidden_view(
        ForbiddenViews, attr="forbidden", renderer="pyramid_fullauth:resources/templates/403.mako"
    )
    configurator.add_forbidden_view(ForbiddenViews, attr="forbidden_json", xhr=True, renderer="json")

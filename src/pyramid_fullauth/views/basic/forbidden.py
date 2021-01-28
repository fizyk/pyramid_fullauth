# Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Forbidden views."""

from pyramid.view import forbidden_view_config
from pyramid.httpexceptions import HTTPFound

from pyramid_fullauth.views import BaseView


class ForbiddenViews(BaseView):
    """Forbidden related views."""

    def __init__(self, request):
        """Set all responses status to 403 by default."""
        super().__init__(request)
        self.request.response.status_code = 403

    @forbidden_view_config(renderer="pyramid_fullauth:resources/templates/403.mako")
    def forbidden(self):
        """Forbidden page view."""
        # do not allow a user to login if they are already logged in
        if self.request.authenticated_userid:
            return {}

        loc = self.request.route_path("login", _query=(("after", self.request.path),))
        return HTTPFound(location=loc)

    @forbidden_view_config(xhr=True, renderer="json")
    def forbidden_json(self):
        """Forbidden xhr response."""
        # do not allow a user to login if they are already logged in
        if self.request.authenticated_userid:
            return {
                "status": False,
                "msg": self.request._(
                    "forbidden-notallowed",
                    default="You are not allowed to use this function",
                    domain="pyramid_fullauth",
                ),
            }

        return {
            "status": False,
            "msg": self.request._(
                "forbidden-login",
                default="You have to be logged in to use this function",
                domain="pyramid_fullauth",
            ),
            "login_url": self.request.route_path("login"),
        }

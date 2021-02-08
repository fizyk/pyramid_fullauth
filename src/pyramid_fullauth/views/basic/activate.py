# Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""Registration related views."""

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPRedirection
from pyramid.security import NO_PERMISSION_REQUIRED

from sqlalchemy.orm.exc import NoResultFound
import pyramid_basemodel

from pyramid_fullauth.views import BaseView
from pyramid_fullauth.models import User
from pyramid_fullauth.events import AfterActivate


@view_config(
    route_name="register:activate",
    permission=NO_PERMISSION_REQUIRED,
    renderer="pyramid_fullauth:resources/templates/activate.mako",
)
class ActivateView(BaseView):
    """Activate account views."""

    def __call__(self):
        """Process account activation."""
        activate_hash = self.request.matchdict.get("hash")
        user = None
        response = {}
        response["status"] = True
        if activate_hash:
            try:
                user = pyramid_basemodel.Session.query(User).filter(User.activate_key == activate_hash).one()
                if not user.is_active:
                    user.is_active = True
            except NoResultFound:
                response["status"] = False
        try:
            self.request.registry.notify(AfterActivate(self.request, user))
        except HTTPRedirection as ex:
            # it's a redirect, let's follow it!
            return ex

        return response

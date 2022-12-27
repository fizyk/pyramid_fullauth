"""Fullauth Security Policy."""
# Based on: https://docs.pylonsproject.org/projects/pyramid/en/latest/whatsnew-2.0.html#upgrading-from-built-in-policies
from typing import Dict, Optional

from pyramid.authentication import AuthTktCookieHelper
from pyramid.authorization import ACLHelper, Authenticated, Everyone
from pyramid.request import Request

from pyramid_fullauth.auth import groupfinder


class FullAuthSecurityPolicy:
    """Fullauth Security Policy."""

    def __init__(self, authtkt_settings: Dict) -> None:
        """Initialise fullauth security."""
        self.helper = AuthTktCookieHelper(**authtkt_settings)

    def identity(self, request: Request) -> Optional[Dict]:
        """Get user identity."""
        # define our simple identity as None or a dict with userid and principals keys
        userid = self.authenticated_userid(request)

        # verify the userid, just like we did before with groupfinder
        principals = groupfinder(userid, request)

        # assuming the userid is valid, return a map with userid and principals
        if principals is not None:
            return {
                "userid": userid,
                "principals": principals,
            }
        return None

    def authenticated_userid(self, request: Request):
        """Load userid."""
        identity = self.helper.identify(request)
        if identity is None:
            return None
        return identity["userid"]  # identical to the deprecated request.unauthenticated_userid

    def permits(self, request: Request, context, permission):
        """
        Build a list of principals.

        Pass them to the ACLHelper to determine allowed/denied
        """
        identity = request.identity
        principals = set([Everyone])
        if identity is not None:
            principals.add(Authenticated)
            principals.add(identity["userid"])
            principals.update(identity["principals"])
        return ACLHelper().permits(context, principals, permission)

    def remember(self, request: Request, userid, **kw):
        """Remember user."""
        return self.helper.remember(request, userid, **kw)

    def forget(self, request: Request, **kw):
        """Forget user."""
        return self.helper.forget(request, **kw)

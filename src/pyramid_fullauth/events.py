# Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT

"""pyramid_fullauth emits these events during whole cycle."""


class _BaseRegisterEvent(object):
    """
    Base fullauth event.

    most of the fullauth's event will provide both request and user
    object with some additional data (these will be described then).
    """

    def __init__(self, request, user):
        """
        Initialize event.

        :param pyramid.request.Request request: request object
        :param pyramid_fullauth.models.User user: user object
        """
        self.request = request
        self.user = user


class BeforeRegister(_BaseRegisterEvent):
    """
    Execute custom code at the start of registration process.

    .. note::

        User object is not yet in session.
    """

    def __init__(self, request, user, errors):
        """
        Initialize event.

        :param pyramid.request.Request request: request object
        :param pyramid_fullauth.models.User user: user object
        :param dict errors: a dictionary with wrong/not submitted fields
            with format - fields for which error occured: error message
        """
        _BaseRegisterEvent.__init__(self, request, user)
        self.errors = errors


class AfterRegister(_BaseRegisterEvent):
    """
    Add custom post-processing code in registration process.

    Can be used to add e.g. e-mail sending with registration links.

    .. note::
        User object is already in a session.

    .. note::
        Action emitting this event, should catch all HTTPRedirection that might
        be risen in event listener.

    .. warning::
        If HTTPRedirection is risen from event listener, then response_values
        will not be used!

    """

    def __init__(self, request, user, response_values):
        """
        Initialize event.

        :param pyramid.request.Request request: request object
        :param pyramid_fullauth.models.User user: user object
        :param dict response_values: a dictionary with response values
        """
        _BaseRegisterEvent.__init__(self, request, user)
        self.response_values = response_values


class AfterActivate(_BaseRegisterEvent):
    """
    Add custom post-processing logic after user gets activated.

    .. note::
        Action emitting this event, should catch all HTTPRedirection that might
        be risen in event listener.
    """


class AfterResetRequest(_BaseRegisterEvent):
    """
    Add custom post-processing after user sends request to reset password.

    .. note::
        Action emitting this event, should catch all HTTPRedirection that might
        be risen in event listener.
    """


class BeforeReset(_BaseRegisterEvent):
    """Add custom pre-processing before the actual reset-password process."""


class AfterReset(_BaseRegisterEvent):
    """
    Add custom post-processing after the actual reset-password process.

    .. note::
        Action emitting this event, should catch all HTTPRedirection that might
        be risen in event listener.
    """


class AlreadyLoggedIn(object):
    """
    Allow execute custom logic, when logged in user tries to log in again.

    .. note::
        Action emitting this event, should catch all HTTPRedirection that might
        be risen in event listener.

    """

    def __init__(self, request):
        """
        Initialize event.

        :param pyramid.request.Request request: request object
        """
        self.request = request


class BeforeLogIn(_BaseRegisterEvent):
    """
    Add custom logic before user gets logged in.

    .. note::
        Action emitting this event, should catch all AttributeError that might
        be risen in event listener.
        User param set to None when user is not found or request method is GET.
    """


class AfterLogIn(_BaseRegisterEvent):
    """Add custom logic after user logs in."""


# Social events
class _BaseSocialRegister(_BaseRegisterEvent):
    """Base for all social requests."""

    def __init__(self, request, user, profile):
        """
        Initialize base events.

        :param pyramid.request.Request request: request object
        :param pyramid_fullauth.models.User user: user object
        :param dict profile: a dictionary with profile data
        """
        _BaseRegisterEvent.__init__(self, request, user)
        self.profile = profile


class BeforeSocialRegister(_BaseSocialRegister):
    """Adds custom logic before the social login process start."""


class AfterSocialRegister(_BaseSocialRegister):
    """
    Add custom logic after user registers through social network.

    .. note::
        Action emitting this event, should catch all HTTPRedirection that might
        be risen in event listener.
    """

    def __init__(self, request, user, profile, response_values):
        """
        Initialize event.

        :param pyramid.request.Request request: request object
        :param pyramid_fullauth.models.User user: user object
        :param dict profile: a dictionary with profile data
        :param dict response_values: a dictionary with response values
        """
        _BaseSocialRegister.__init__(self, request, user, profile)
        self.response_values = response_values


class AfterSocialLogIn(_BaseSocialRegister):
    """
    Custom logic after user logs in through social network.

    .. note::
        Action emitting this event, should catch all HTTPRedirection that might
        be risen in event listener.
    """


class SocialAccountAlreadyConnected(_BaseSocialRegister):
    """
    Event raised when social account is already connected to some other user.

    Allow to add custom logic, when someone tries to connect social account to
    second user in application.

    .. note::
        Action emitting this event, should catch all HTTPRedirection that might
        be risen in event listener.
    """

    def __init__(self, request, user, profile, response_values):
        """
        Initialize event.

        :param pyramid.request.Request request: request object
        :param pyramid_fullauth.models.User user: user object
        :param dict profile: a dictionary with profile data
        :param dict response_values: a dictionary with response values
        """
        _BaseSocialRegister.__init__(self, request, user, profile)
        self.response_values = response_values


# Email change events.


class BeforeEmailChange(_BaseRegisterEvent):
    """Allow to add custom validation (like checking password) before email change process."""


class AfterEmailChange(_BaseRegisterEvent):
    """Allow to add some custom post-processing, like e-mail sending, after email change process."""


class AfterEmailChangeActivation(_BaseRegisterEvent):
    """Allow to add custom logic, after changed email had been activated."""

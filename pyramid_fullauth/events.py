# -*- coding: utf-8 -*-

# Copyright (c) 2013 by pyramid_fullauth authors and contributors <see AUTHORS file>
#
# This module is part of pyramid_fullauth and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT

'''
    pyramid_fullauth emits these events during whole cycle.
'''


class _BaseRegisterEvent(object):

    '''
        Base fullauth - most of the fullauth's event will provide both request and suer object with some additional data (these will be described then)
    '''

    def __init__(self, request, user):
        '''

            :param pyramid.request.Request request: request object
            :param pyramid_fullauth.models.User user: user object
        '''
        self.request = request
        self.user = user


class BeforeRegister(_BaseRegisterEvent):

    '''
        BeforeRegister event, fired, so developers can add custom validation
        User object is not yet defined
    '''

    def __init__(self, request, user, errors):
        '''

            :param pyramid.request.Request request: request object
            :param pyramid_fullauth.models.User user: user object
            :param dict errors: a dictionary with wrong/not submitted fields
             with format - fields for which error occured: error message
        '''

        _BaseRegisterEvent.__init__(self, request, user)
        self.errors = errors


class AfterRegister(_BaseRegisterEvent):

    '''
        AfterRegister event, fired so developers can add some custom post-processing, like e-mail sending
        User object is already in a session.

        .. note::
            Action emitting this event, should catch all HTTPFound that might be risen in event listener.

        .. warning::
            If HTTPFound is risen from event listener, then response_values will not be used!

    '''

    def __init__(self, request, user, response_values):
        '''

            :param pyramid.request.Request request: request object
            :param pyramid_fullauth.models.User user: user object
            :param dict response_values: a dictionary with response values
        '''
        _BaseRegisterEvent.__init__(self, request, user)
        self.response_values = response_values


class AfterActivate(_BaseRegisterEvent):

    '''
        Events gets emitted after account activation. To send a greeting email, or other actions that could be taken

        .. note::
            Action emitting this event, should catch all HTTPFound that might be risen in event listener.
    '''
    pass


class AfterResetRequest(_BaseRegisterEvent):

    '''
        Event gets fired when the user requires password reset

        .. note::
            Action emitting this event, should catch all HTTPFound that might be risen in event listener.
    '''
    pass


class BeforeReset(_BaseRegisterEvent):

    '''
        Event gets fired when user resets own password, fired so developer can add custom validation (like password length)
    '''
    pass


class AfterReset(_BaseRegisterEvent):

    '''
        Event gets fired when user resets own password

        .. note::
            Action emitting this event, should catch all HTTPFound that might be risen in event listener.
    '''
    pass


class AlreadyLoggedIn(object):

    '''
        Event gets fired when the logged in user enters login page

        .. note::
            Action emitting this event, should catch all HTTPFound that might be risen in event listener.
    '''

    def __init__(self, request):
        '''
            :param pyramid.request.Request request: request object
        '''
        self.request = request


class BeforeLogIn(_BaseRegisterEvent):

    '''
        Event gets fired before the user logs in

        .. note::
            Action emitting this event, should catch all AttributeError that might be risen in event listener.
            User param set to None when user is not found or request method is GET.
    '''
    pass


class AfterLogIn(_BaseRegisterEvent):

    '''
        Event gets fired when the user logs in
    '''
    pass


# Social events
# TODO: extract to sub module


class _BaseSocialRegister(_BaseRegisterEvent):

    '''
        Base for all social requests
    '''

    def __init__(self, request, user, profile):
        '''

            :param pyramid.request.Request request: request object
            :param pyramid_fullauth.models.User user: user object
            :param dict profile: a dictionary with profile data
        '''
        _BaseRegisterEvent.__init__(self, request, user)
        self.profile = profile


class BeforeSocialRegister(_BaseSocialRegister):

    '''
        BeforeRegister event, fired, so developers can add custom validation
    '''
    pass


class AfterSocialRegister(_BaseSocialRegister):

    '''
        AfterSocialRegister events is emitted after user registers through one of the social networks

        .. note::
            Action emitting this event, should catch all HTTPFound that might be risen in event listener.
    '''

    def __init__(self, request, user, profile, response_values):
        '''

            :param pyramid.request.Request request: request object
            :param pyramid_fullauth.models.User user: user object
            :param dict profile: a dictionary with profile data
            :param dict response_values: a dictionary with response values
        '''
        _BaseSocialRegister.__init__(self, request, user, profile)
        self.response_values = response_values


class AfterSocialLogIn(_BaseSocialRegister):

    '''
        Event gets fired when the user logs in through social network

        .. note::
            Action emitting this event, should catch all HTTPFound that might be risen in event listener.
    '''
    pass


class SocialAccountAlreadyConnected(_BaseSocialRegister):

    '''
        Event gets fired when the user try to connect social network to account but this social account is already connected to another account

        .. note::
            Action emitting this event, should catch all HTTPFound that might be risen in event listener.
    '''

    def __init__(self, request, user, profile, response_values):
        '''

            :param pyramid.request.Request request: request object
            :param pyramid_fullauth.models.User user: user object
            :param dict profile: a dictionary with profile data
            :param dict response_values: a dictionary with response values
        '''
        _BaseSocialRegister.__init__(self, request, user, profile)
        self.response_values = response_values
    pass


class BeforeEmailChange(_BaseRegisterEvent):

    '''
        BeforeEmailChange event, fired so developers can add custom validation (like checking password)
    '''
    pass


class AfterEmailChange(_BaseRegisterEvent):

    '''
        AfterEmailChange event, fired so developers can add some custom post-processing, like e-mail sending
    '''
    pass


class AfterEmailChangeActivation(_BaseRegisterEvent):

    '''
        AfterEmailChangeActivation event, fired when user activate new email addres, so developers can add some custom post-processing
    '''
    pass

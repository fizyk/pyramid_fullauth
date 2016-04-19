## -*- coding: utf-8 -*-
<%doc>
Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>

This module is part of pyramid_fullauth and is released under
the MIT License (MIT): http://opensource.org/licenses/MIT
</%doc>
<%namespace name="social" file="../helpers/social.mako" import="social_auth_uri"/>
<h1>${_('Social login', domain='pyramid_fullauth')}</h1>
% if 'social' in request.registry['config'].fullauth:
    % if 'facebook' in request.registry['config'].fullauth.social:
        <a href="${social.social_auth_uri('facebook', scope=request.registry['config'].fullauth.social.facebook.scope)}">${_('Connect with facebook', domain='pyramid_fullauth')}</a>
    % endif
    % if 'twitter' in request.registry['config'].fullauth.social:
        <a href="${social.social_auth_uri('twitter')}">${_('Connect with twitter', domain='pyramid_fullauth')}</a>
    % endif
% endif

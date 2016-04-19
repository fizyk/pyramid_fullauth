## -*- coding: utf-8 -*-
<%doc>
Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>

This module is part of pyramid_fullauth and is released under
the MIT License (MIT): http://opensource.org/licenses/MIT
</%doc>
<%inherit file="pyramid_fullauth:resources/templates/layout.mako" />
% if not status:
    <h1>${_('Invalid activation code', domain='pyramid_fullauth')}</h1>
% else:
    <h1>${_('Thank you for activating your account!', domain='pyramid_fullauth')}</h1>
    <p>${_('And welcome to our site!', domain='pyramid_fullauth')}</p>
% endif

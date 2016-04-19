## -*- coding: utf-8 -*-
<%doc>
Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>

This module is part of pyramid_fullauth and is released under
the MIT License (MIT): http://opensource.org/licenses/MIT
</%doc>
<%inherit file="pyramid_fullauth:resources/templates/layout.mako" />
<h1>${_('Please, log in', domain='pyramid_fullauth')}:</h1>
% if not status:
    <div class="alert alert-error">${_('Error!', domain='pyramid_fullauth')} ${msg}</div>
% endif
<%include file="_form.login.mako"/>
<%include file="_social.login.mako"/>

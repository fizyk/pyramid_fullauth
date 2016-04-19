## -*- coding: utf-8 -*-
<%doc>
Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>

This module is part of pyramid_fullauth and is released under
the MIT License (MIT): http://opensource.org/licenses/MIT
</%doc>
<%inherit file="pyramid_fullauth:resources/templates/layout.mako" />
<h1>${_('Please, register', domain='pyramid_fullauth')}:</h1>
% if errors:
    <div class="alert alert-error">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <strong>${_('Error!', domain='pyramid_fullauth')}</strong> ${msg}
    </div>
% elif not request.method == 'GET':
    <div class="alert alert-success">
      <button type="button" class="close" data-dismiss="alert">x</button>
      <strong>${_('Success!', domain='pyramid_fullauth')}</strong> ${_('You have sucessfully registered', domain='pyramid_fullauth')}
    </div>
% endif
<%include file="_form.register.mako"/>
<%include file="_social.login.mako"/>

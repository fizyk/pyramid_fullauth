## -*- coding: utf-8 -*-
<%doc>
Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>

This module is part of pyramid_fullauth and is released under
the MIT License (MIT): http://opensource.org/licenses/MIT
</%doc>
<%inherit file="pyramid_fullauth:resources/templates/layout.mako" />

<h1>${_('Recover your password', domain='pyramid_fullauth')}</h1>
<div class="row-fluid">
    <div class="span2"></div>
    <div class="span8">
        % if not status:
            <div class="alert alert-error">${_('Error!', domain='pyramid_fullauth')} ${msg}</div>
        % endif
        <form class="form-horizontal" name="reset_password" method="POST" action="${request.current_route_path()}">
            <fieldset>
                <div class="control-group">
                    <label class="control-label" for="reset[email]">${_('Your e-mail address', domain='pyramid_fullauth')}:</label>
                    <div class="controls">
                        <input type="email" placeholder="username@hostname.com" name="email" id="reset[email]"/>
                        <input type="hidden" name="csrf_token" value="${csrf_token}" />
                    </div>
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn btn-large">${_('Reset Password', domain='pyramid_fullauth')}</button>
                </div>
            </fieldset>
        </form>
    </div>
    <div class="span2"></div>
</div>


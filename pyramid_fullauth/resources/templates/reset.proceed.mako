## -*- coding: utf-8 -*-
<%doc>
Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>

This module is part of pyramid_fullauth and is released under
the MIT License (MIT): http://opensource.org/licenses/MIT
</%doc>
<%inherit file="pyramid_fullauth:resources/templates/layout.mako" />

<h1>${_('Recover your password - choose new password', domain='pyramid_fullauth')}</h1>
<div class="row-fluid">
    <div class="span8">
        % if not status:
            <div class="alert alert-error">${_('Error!', domain='pyramid_fullauth')} ${msg}</div>
        % endif
        <form class="form-horizontal" id="reset_password" name="reset_password" method="POST" action="${request.current_route_path()}">
            <input type="hidden" name="csrf_token" value="${csrf_token}" />
            <fieldset>
                <div class="control-group">
                    <label class="control-label" for="password">${_('Password', domain='pyramid_fullauth')}:</label>
                    <div class="controls">
                        <input type="password" id="password" name="password" placeholder="minimum 6 characters"/>
                        <span class="help-inline" id="password_status"></span>
                    </div>
                </div>
                <div class="control-group">
                    <label class="control-label" for="confirm_password">${_('Confirm password', domain='pyramid_fullauth')}:</label>
                    <div class="controls">
                        <input type="password" name="confirm_password" id="confirm_password"/>
                        <span class="help-inline" id="confirm_password_status"></span>
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


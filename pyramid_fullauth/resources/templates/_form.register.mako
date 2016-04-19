## -*- coding: utf-8 -*-
<%doc>
Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>

This module is part of pyramid_fullauth and is released under
the MIT License (MIT): http://opensource.org/licenses/MIT
</%doc>
<form class="registerForm" id="register_form" name="register_form" method="POST" action="${request.route_path('register')}">
    <input type="hidden" name="csrf_token" value="${csrf_token}" />
    <fieldset>
        <div class="control-group ${'error' if 'email' in errors else ''}">
            <label class="control-label">${_('E-mail', domain='pyramid_fullauth')}:</label>
            <div class="controls">
                <input id="email" placeholder="username@hostname.com" type="email" name="email" required="required" value="${request.params.get('email','')}" />
                % if 'email' in errors:
                    <span class="help-inline">${errors['email']}</span>
                % endif
            </div>
        </div>
        <div class="control-group ${'error' if 'password' in errors else ''}">
            <label class="control-label">${_('Password', domain='pyramid_fullauth')}:</label>
            <div class="controls">
                <input type="password" id="password" name="password" required="required"/>
                % if 'password' in errors:
                    <span class="help-inline">${errors['password']}</span>
                % endif
            </div>
        </div>
        <%
            password_options = request.registry['config'].fullauth.register.password
        %>
        % if password_options['confirm']:
            <div class="control-group ${'error' if 'confirm_password' in errors else ''}">
                <label class="control-label">${_('Confirm password', domain='pyramid_fullauth')}:</label>
                <div class="controls">
                    <input type="password" name="confirm_password" id="confirm_password" required="required"/>
                    % if 'confirm_password' in errors:
                        <span class="help-inline">${errors['confirm_password']}</span>
                    % endif
                </div>
            </div>
        % endif
        <div>
            <button id="submit_register" type="submit" class="btn btn-primary btn-large"><strong>${_('Sign up', domain='pyramid_fullauth')}</strong></button>
        </div>
    </fieldset>
</form>

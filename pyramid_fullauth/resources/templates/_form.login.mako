## -*- coding: utf-8 -*-
<%doc>
Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>

This module is part of pyramid_fullauth and is released under
the MIT License (MIT): http://opensource.org/licenses/MIT
</%doc>
<form id="login_form" name="login_form" method="POST" action="${request.route_path('login')}">
    <fieldset>
        <div class="control-group">
            <label class="control-label">${_('E-mail', domain='pyramid_fullauth')}:</label>
            <div class="controls">
                <input type="email" placeholder="username@hostname.com" name="email"  class="input-xlarge"/>
            % if after:
                <input type="hidden" name="after" value="${after}" />
            % endif
                <input type="hidden" name="csrf_token" value="${csrf_token}" />
            </div>
        </div>
        <div class="control-group">
            <label class="control-label">${_('Password', domain='pyramid_fullauth')}:</label>
            <div class="controls">
                <input type="password" name="password" class="input-xlarge"/>
            </div>
        </div>
        <div class="control-group">
            <label class="control-label">${_('Remember me', domain='pyramid_fullauth')}:</label>
            <div class="controls">
                <input type="checkbox" name="remember" value="1" />
            </div>
        </div>
        <div class="control-group">
            <div class="controls options">
                <a href="${request.route_path('password:reset')}">${_('Forgot your password, right?', domain='pyramid_fullauth')}</a><br/>
                <a id="sign_up_login" href="${request.route_path('register')}">${_('Want to join? Sign Up!', domain='pyramid_fullauth')}</a><br/>
            </div>
        </div>
        <div class="modal-footer center">
            <div>
                <button type="submit" class="btn btn-primary btn-large f18 w180"><strong>${_('Log in', domain='pyramid_fullauth')}</strong></button>
            </div>
        </div>
    </fieldset>
</form>

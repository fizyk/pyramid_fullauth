<form id="login_form" name="login_form" method="POST" action="${request.route_path('login')}">
    <fieldset>
        <div class="control-group">
            <label class="control-label">E-mail:</label>
            <div class="controls">
                <input type="email" placeholder="username@hostname.com" name="email"  class="input-xlarge"/>
            % if after:
                <input type="hidden" name="after" value="${after}" />
            % endif
                <input type="hidden" name="token" value="${token}" />
            </div>
        </div>
        <div class="control-group">
            <label class="control-label">Password:</label>
            <div class="controls">
                <input type="password" name="password" class="input-xlarge"/>
            </div>
        </div>
        <div class="control-group">
            <label class="control-label">Remember me:</label>
            <div class="controls">
                <input type="checkbox" name="remember" value="1" />
            </div>
        </div>
        <div class="control-group">
            <div class="controls options">
                <a href="${request.route_path('password:reset')}">Forgot your password, right?</a><br/>
                <a id="sign_up_login" href="${request.route_path('register')}">Want to join? Sign Up!</a><br/>
            </div>
        </div>
        <div class="modal-footer center">
            <div>
                <button type="submit" class="btn btn-primary btn-large f18 w180"><strong>Log in</strong></button>
            </div>
        </div>
    </fieldset>
</form>

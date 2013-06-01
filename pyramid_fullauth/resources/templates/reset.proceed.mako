<%inherit file="pyramid_fullauth:resources/templates/layout.mako" />

<h1>Recover your password - choose new password</h1>
<div class="row-fluid">
    <div class="span8">
        % if not status:
            <div class="alert alert-error">Error! ${msg}</div>
        % endif
        <form class="form-horizontal" id="reset_password" name="reset_password" method="POST" action="${request.current_route_path()}">
            <input type="hidden" name="token" value="${token}" />
            <fieldset>
                <div class="control-group">
                    <label class="control-label" for="password">Password:</label>
                    <div class="controls">
                        <input type="password" id="password" name="password" placeholder="minimum 6 characters"/>
                        <span class="help-inline" id="password_status"></span>
                    </div>
                </div>
                <div class="control-group">
                    <label class="control-label" for="confirm_password">Confirm password:</label>
                    <div class="controls">
                        <input type="password" name="confirm_password" id="confirm_password"/>
                        <span class="help-inline" id="confirm_password_status"></span>
                    </div>
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn btn-large">Reset Password</button>
                </div>
            </fieldset>
        </form>
    </div>
    <div class="span2"></div>
</div>


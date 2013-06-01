<%inherit file="pyramid_fullauth:resources/templates/layout.mako" />
<h1>Please, register:</h1>
% if errors:
    <div class="alert alert-error">
        <button type="button" class="close" data-dismiss="alert">×</button>
        <strong>Error!</strong>${msg}
    </div>
    % if 'token' in errors:
        <div class="alert alert-error">
            <button type="button" class="close" data-dismiss="alert">×</button>
            <strong>CSRF Attack detected!</strong>${errors['token']}
        </div>
    % endif
% elif not request.method == 'GET':
    <div class="alert alert-success">
      <button type="button" class="close" data-dismiss="alert">×</button>
      <strong>Success!</strong> You have sucessfully registered
    </div>
% endif
<%include file="_form.register.mako"/>
<%include file="_social.login.mako"/>

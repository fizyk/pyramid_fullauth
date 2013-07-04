<%inherit file="pyramid_fullauth:resources/templates/layout.mako" />
<h1>${_('Please, register', domain='pyramid_fullauth')}:</h1>
% if errors:
    <div class="alert alert-error">
        <button type="button" class="close" data-dismiss="alert">x</button>
        <strong>${_('Error!', domain='pyramid_fullauth')}</strong> ${msg}
    </div>
    % if 'token' in errors:
        <div class="alert alert-error">
            <button type="button" class="close" data-dismiss="alert">x</button>
            <strong>${_('CSRF Attack detected!', domain='pyramid_fullauth')}</strong> ${errors['token']}
        </div>
    % endif
% elif not request.method == 'GET':
    <div class="alert alert-success">
      <button type="button" class="close" data-dismiss="alert">x</button>
      <strong>${_('Success!', domain='pyramid_fullauth')}</strong> ${_('You have sucessfully registered', domain='pyramid_fullauth')}
    </div>
% endif
<%include file="_form.register.mako"/>
<%include file="_social.login.mako"/>

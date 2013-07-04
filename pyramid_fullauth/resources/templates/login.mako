<%inherit file="pyramid_fullauth:resources/templates/layout.mako" />
<h1>${_('Please, log in', domain='pyramid_fullauth')}:</h1>
% if not status:
    <div class="alert alert-error">${_('Error!', domain='pyramid_fullauth')} ${msg}</div>
% endif
<%include file="_form.login.mako"/>
<%include file="_social.login.mako"/>

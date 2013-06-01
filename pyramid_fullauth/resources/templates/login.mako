<%inherit file="pyramid_fullauth:resources/templates/layout.mako" />
<h1>Please, log in:</h1>
% if not status:
    <div class="alert alert-error">Error! ${msg}</div>
% endif
<%include file="_form.login.mako"/>
<%include file="_social.login.mako"/>

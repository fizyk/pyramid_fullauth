<%namespace name="social" file="../helpers/social.mako" import="social_auth_uri"/>
<h1>Social login</h1>
% if 'social' in request.config.fullauth:
    % if 'facebook' in request.config.fullauth.social:
        <a href="${social.social_auth_uri('facebook', scope=request.config.fullauth.social.facebook.scope)}">Connect with facebook</a>
    % endif
    % if 'twitter' in request.config.fullauth.social:
        <a href="${social.social_auth_uri('twitter')}">Connect with twitter</a>
    % endif
% endif

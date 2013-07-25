<%namespace name="social" file="../helpers/social.mako" import="social_auth_uri"/>
<h1>${_('Social login', domain='pyramid_fullauth')}</h1>
% if 'social' in request.config.fullauth:
    % if 'facebook' in request.config.fullauth.social:
        <a href="${social.social_auth_uri('facebook', scope=request.config.fullauth.social.facebook.scope)}">${_('Connect with facebook', domain='pyramid_fullauth')}</a>
    % endif
    % if 'twitter' in request.config.fullauth.social:
        <a href="${social.social_auth_uri('twitter')}">${_('Connect with twitter', domain='pyramid_fullauth')}</a>
    % endif
% endif

<%def name="social_auth_uri(name, **kw)">
<%
    from velruse import login_url
    import urllib
%>
% if name in request.config.fullauth.social:
${login_url(request, name) + ('?{0}'.format(urllib.urlencode(kw)) if kw else '')}
% endif
</%def>

## -*- coding: utf-8 -*-
<%doc>
Copyright (c) 2013 - 2014 by pyramid_fullauth authors and contributors <see AUTHORS file>

This module is part of pyramid_fullauth and is released under
the MIT License (MIT): http://opensource.org/licenses/MIT
</%doc>

<%def name="social_auth_uri(name, **kw)">
<%
    from velruse import login_url
    import urllib
%>
% if name in request.registry['config'].fullauth.social:
${login_url(request, name) + ('?{0}'.format(urllib.urlencode(kw)) if kw else '')}
% endif
</%def>

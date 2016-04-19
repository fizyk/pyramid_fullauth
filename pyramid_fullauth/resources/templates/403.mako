## -*- coding: utf-8 -*-
<%doc>
Copyright (c) 2013 - 2016 by pyramid_fullauth authors and contributors <see AUTHORS file>

This module is part of pyramid_fullauth and is released under
the MIT License (MIT): http://opensource.org/licenses/MIT
</%doc>
<%inherit file="pyramid_fullauth:resources/templates/layout.mako" />

<h1>HTTP://403</h1>
<p>${_('Sorry, we couldn\'t serve you this, your clearance code is too low!', domain='pyramid_fullauth')}</p>

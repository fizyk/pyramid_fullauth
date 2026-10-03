Customisation
=============

To overwrite templates provided in ``pyramid_fullauth`` just add this line to your project's init script:

.. code-block:: python

    config.override_asset(
        to_override='pyramid_fullauth:resources/templates/layout.mako',
        override_with='mypackage:path/to/template/layout.html')

You can overwrite all templates separately, all by a group, for more information, read:
http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/assets.html#overriding-assets

Root factory
------------

``pyramid_fullauth`` registers its own root factory
(:class:`pyramid_fullauth.auth.BaseACLRootFactoryMixin`) automatically, so the
ACL machinery is available out of the box. To use your own root factory
instead (for example one that adds custom context classes), register it as a
utility for ``pyramid.interfaces.IRootFactory`` *after* including the plugin:

.. code-block:: python

    config.include('pyramid_fullauth')
    config.registry.registerUtility(MyRootFactory, IRootFactory)

The plugin only registers its own factory when none is present, so registering
yours afterwards guarantees it wins. ``MyRootFactory`` is free to inherit from
:class:`pyramid_fullauth.auth.BaseACLRootFactoryMixin` to keep the built-in ACL
behaviour::

    from pyramid_fullauth.auth import BaseACLRootFactoryMixin

    class MyRootFactory(BaseACLRootFactoryMixin):
        def __init__(self, request):
            super().__init__(request)
            # custom context setup...

Form inclusion
--------------

You might want to just include form on some pages. all form templates that can be included are prefixed with '_form':


.. code-block:: mako

    <%include file="pyramid_fullauth:resources/templates/_form.login.mako"/>

Customisation
=============

To overwrite templates provided in ``pyramid_fullauth`` just add this line to your project's init script:

.. code-block:: python

    config.override_asset(
        to_override='pyramid_fullauth:resources/templates/layout.mako',
        override_with='mypackage:path/to/template/layout.html')

You can overwrite all templates separately, all by a group, for more information, read:
http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/assets.html#overriding-assets

Form inclusion
--------------

You might want to just include form on some pages. all form templates that can be included are prefixed with '_form':


.. code-block:: mako

    <%include file="pyramid_fullauth:resources/templates/_form.login.mako"/>

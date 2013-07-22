Advanced configuration
======================

Authentication policy
---------------------

registerlogin uses **AuthTktAuthenticationPolicy**. It's default settings are stored within config as:


.. code-block:: yaml

    registerlogin:
        AuthTkt:
            secret: fullauth_psst # default secret used to hash auth_tk cookie
            hashalg: sha512             # default authentication policy hash algorithm
            timeout: 2              # (optional) number of seconds for which an auth ticket will be valid
            reissue_time: 0.2  # (optional) number of seconds that must pass before an authentication token cookie is automatically reissued as the result of a request which requires authentication

.. note::

  **timeout** and **reissue_time** settings indicate after which period of time user will be logged out in case of inactivity. If not included in your AuthTktAuthenticationPolicy config, default value for them will be None.
  To get a better insight on how they work when they are set, look at **tests.test_login**: **test_automatic_logout** and **test_automatic_logout_not_expired** test cases.

.. seealso::
   For more information about additional settings that could be included in your AuthTktAuthenticationPolicy
   as well as how to set optimal values for timeout and reissue_time please see :class:`~pyramid.authentication.AuthTktAuthenticationPolicy`.

   .. warning::
      **callback** setting is already defined by registerlogin as :meth:`pyramid_fullauth.auth.groupfinder`.

.. note::

   To restrict subdomain applications from using the same cookie, use **registerlogin.AuthTkt.wild_domain setting**, and set it to False.
   This will restrict emitted cookies to current domain only.
   You can also change settings as **registerlogin.AuthTkt.cookie_name** and **registerlogin.AuthTkt.secret** to make sure, your apps will use different cookie names and salts.


Authentication Providers
------------------------

Might happen, that the project needs to identify what authentication providers is user using (Might use e.g facebook, google, email, some OpenID). That's what the user.providers relation is for.

It stores data needed to authenticate with different providers for each user, but the exception is email, where user is identified by id in a system. Each of the social providers entry gets added by connecting user account with given social network, and the email entry during standard registration or during reset password.


ACL
---

``pyramid_fullauth`` package provides also a basic ACL Mixin for your RootFactory. it contains basic acl definition as well as init method.

See :class:`pyramid_fullauth.auth.BaseACLRootFactoryMixin`


Events
------

Plugin emits several events throughout the registration process, login and several other actions.

All of them, along with details description can be found in the :mod:`pyramid_fullauth.events` package.

Read the :ref:`events_chapter` chapter of Pyramid's documentation to see how to add an event subscriber to Your application and handle those events.


Session Factory
---------------

*pyramid_fullauth* allows you to connect custom session factory within application, by default, it uses pyramid's :func:`~pyramid.session.UnencryptedCookieSessionFactoryConfig`, but using different session factory is just a matter of appropriate settings in **fullauth.session**. See :ref:`configuration` section on how to configure.

More on sessions and session factory can be read in _ :ref:`sessions_chapter` chapter of Pyramid's documentation

Social register and login
=========================

Module provides register and login funcion using social sites such as facebook or twitter.
Those actions use velruse library for unification of different authentication providers.
Now only facebook and twitter were tested, but this library offers many more.


Configuration
-------------

Plugin creates login/register views for auth providers provided in config file.
Below is example for facebook, you can check required configuration for other providers here: https://velruse.readthedocs.org/en/latest/

.. code-block:: ini

    fullauth.social.facebook.consumer_key = some_key
    fullauth.social.facebook.consumer_secret = some_secret
    fullauth.social.facebook.scope = mail,offline_access

Usage
-----

In default views for register and login there are links in **Social login** section. If you want to show those buttons somewhere else you can
do this by
importing function for creating urls:

.. code-block:: mako

    <%namespace name="social" file="pyramid_fullauth:resources/helpers/social.mako" import="social_auth_uri"/>

and puting one of those links in your templates:

.. code-block:: mako

    <a href="${social.social_auth_uri('facebook', scope=request.registry["fullauth"]["social"]["facebook"]["scope"])}">Connect with facebook</a>
    <a href="${social.social_auth_uri('twitter')}">Connect with twitter</a>

Events
------

Plugin emits three events only for social login: :doc:`api/events`

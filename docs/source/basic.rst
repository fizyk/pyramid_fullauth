Basics
======

``pyramid_fullauth`` provides models and actions that allows to register and log in user as well as reset password functionality.
It does not provide ability to send appropriate emails, that have to be covered by subscribing to appropriate events emitted by plugin.

.. note::

    By default, all actions are unrestricted (have permissions set to pyramid.security.NO_PERMISSION_REQUIRED, that way setting default permission in your pyramid app would allow the user to log in, register without the need to being logged in to the system

Simple usage
------------

If You have a ``sqlalchemy.url`` key in the config file In Your pyramid
application configuration section just add those two lines:

.. code-block:: python

    config.include('pyramid_basemodel')
    config.include('pyramid_fullauth')

And that's it, this is the most simple usage of this plugin. To register just
go to the **/register** url and You will see the form with which You can
register. Login in is performed on **/login** page

**pyramid_fullauth** uses under the hood **pyramid_yml** to include configuration defaults defined in yaml file, and to override them, you'd have to employ pyramid_yml on your own into the project.


Events and event interfaces
---------------------------

Plugin emits events while handling requests:

.. code-block:: rest

   BeforeRegister
   AfterRegister
   AfterActivate
   AfterResetRequest
   AfterReset
   AlreadyLoggedIn
   BeforeLogIn
   AfterLogIn

Events can be found in the :mod:`pyramid_fullauth.events` package.

Read the :ref:`events_chapter` chapter of Pyramid's documentation to see how to add an event subscriber to Your application and handle those events.


.. _configuration:

Configuration
-------------

.. note::
    Plugins uses `tzf.pyramid_yml <https://tzfpyramid_yml.readthedocs.org/en/latest/>`_ for its configuration settings

Plugin, by default works on these assumptions:

.. literalinclude:: ../../pyramid_fullauth/config/default.yaml
    :language: yaml
    :linenos:

.. note::
    For alternative values of the settings above look at config.{env}.yml configurations found in tests.config directory.

Fullauth data models
--------------------

**pyramid_fullauth** comes with `SQLAlchemy <http://www.sqlalchemy.org/>`_ models to maintain the user data.

* :class:`pyramid_fullauth.models.User` - is the base model with most relevant user data
* :class:`pyramid_fullauth.models.Group` - allows grouping user in permission groups
* :class:`pyramid_fullauth.models.AuthenticationProvider` - is where the 3rd party authentication system identifiers for different providers lives

Fullauth models are based on declarative_base defined in `pyramid_basemodel
<https://github.com/thruflo/pyramid_basemodel>`_ and functionality uses Session object provided
by basemodel.

To connect fullauth's models to your database, it is required to base your own models on the same
declarative_base. It can be achieved by either using those provided by pyramid_basemodel or patching
them with your own.

Last thing is updating the database. If you're using alembic for that, remember to import fullauth
models in alembic's env,py or in common place for your model. If models won't be imported while
running alembic commands, they won't be seen by alembic.

Request object additional methods
---------------------------------

Request object gets these methods:

- :meth:`~pyramid_fullauth.request.login_perform` - performs login action
- :meth:`~pyramid_fullauth.request.user` - returns logged in user or None
- :meth:`~pyramid_fullauth.request.logout` - logs user out

CSRF Check
----------

CSRF can be turned on/off for fullauth views by modifying *fullauth.check_csrf* key. It's turned on by default.

pyramid_fullauth extends pyrmid's check_csrf predicate in that way, that you can turn it on and off, and when check fails, it raises :class:`~pyramid.httpexceptions.HTTPUnauthorized` exception instead of returning False, which gives usually 404 Not Found error


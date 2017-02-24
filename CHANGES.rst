CHANGELOG
=========

0.6.0
-------

- increased the size of password and salt fields to 128 characters each
- default password hashing algorithm is sha256

0.5.0
-------

- full python3 compatibility, since velruse migrated to py3 enabled requests-oauth
- require velruse 1.1.1
- run tests with sqlalchemy 1.0.x
- small updates to conform with new linters versions embedded in pylama

0.4.1
-------

- fixed spelling for error message when user does not exist while trying to reset password.
- require pyramid_basemodel at least version 0.3

0.4.0
-------

- python 3 compatibility (without oauth2 though)
- cleared use of deprecated function `pyramid.security.authenticated_userid` in favour of `pyramid.request.Request.authenticated_userid` attribute.
- make email fields case insensitive by using hybrid properties and CaseInsensitive comparator for model.

0.3.3
-------

- Fix issue where groupfined was returning empty list instead of None when user did not existed

0.3.2
-----

- catch all HTTPRedirect instead of just HTTPFound.
- redirect with HTTPSeeOther instead of HTTPFound where applicable.


0.3.1
-----

- fixes MANIFEST.in to include yaml files - fixes `#33 <https://github.com/fizyk/pyramid_fullauth/issues/33>`_.

0.3.0
-----

Features
++++++++

- configure root factory if it hasn't been already done
- configure session factory only if it hasn't been configured before
- configure authorization policy only if it hasn't been configured before
- configure authentication policy only if it hasn't been configured before
- logged in user will be redirected always away from login page
- views reorganisation - grouping by their function
- replaced force_logout decorator with logout request method
- small login view simplification

tests
+++++

- rewritten tests to use pytest_pyramid
- unified session with pyramid_basemodel's
- parametrize tests against two most recent pyramid versions and sqlalchemy
- turned on pylama to check code with linters:
    - pep8
    - pep257
    - pyflakes
    - mccabe
- add pytest-dbfixtures, and run tests against postgresql and mysql as well
- drop python 2.6 from tests
- 100% test coverage


0.2.3
-----
- weaker pyramid_yml requirements. Use ``registry['config']`` instead of ``request.config`` which gets added only when explicitly including tzf.pyramid_yml package.
- remove default_config with permission set for forbidden views. Throwning errors in pyramid 1.5a3
- remove lazy='load' for relationship between AuthenticationProvider and User models as it was incorrect. Fixes error while using with sqlalchemy 0.9

0.2.2
-----
- copy all headers when login user. fixes issue, when headers set in AfterLogin event would not get passed

0.2.1
-----
- fixed csrf_check in password:reset:continue action
- updated translation files

0.2.0
-----
- migrated tests to py.test
- removed nose and lxml from test requirements
- extracted UserEmailMixin from User model
- validation exception improvements
- set licensing to MIT License
- fixed general error message for register_POST processing
- activate action no longer gives 404 error after first use. Default is message about token being invalid or used [veronicazgirvaci]
- extending csrf_check predicate:
    - Can be turned on/off in settings.
    - Failed check rises 401 Unauthorised error

Backwards Incompatibilities
+++++++++++++++++++++++++++

- token variable is changed into csrf_token in fullatuh views
- view no longer returns error messages on failed csrf token. Rises 401 Unauthorised error instead.


0.1.0
-----
- add localize to requirements. Ability to translate registerlogin communicates
- ability to set custom session factory [with Veronica Zgirvaci help]
- moved password validation to one place

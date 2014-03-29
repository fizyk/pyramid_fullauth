CHANGELOG
=========

current
-------

tests
+++++

- rewritten tests to use pytest_pyramid
- unified session with pyramid_basemodel's
- parametrize tests against two most recent pyramid versions and sqlalchemy
- add pytest-dbfixtures, and run tests against postgresql and mysql as well


0.2.3
-----
- weaker pyramid_yml requirements. Use ``registry['config']`` instead of ``request.config`` which gets added only whet explicitly including tzf.pyramid_yml package.
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

0.0.4
-----
- remove basemodel restrictions from setup.py

0.0.3
-----
- fixed issue, where reset password would check for csrf on GET request [Veronica Zgirvaci]

0.0.2
-----
- fixed MANIFEST.in, to include .yml, and .mako files

0.0.1
-----
- initial package creation
- prepared for CI on travis-ci, and coverage reports on coveralls.io

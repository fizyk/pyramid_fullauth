=======
CHANGES
=======

CURRENT
-------
- migrated tests to py.test
- removed nose and lxml from test requirements
- extracted UserEmailMixin from User model
- validation exception improvements
- set licensing to MIT License
- fixed general error message for register_POST processing
- activate action no longer gives 404 error after first use. Default is message about token being invalid or used [veronicazgirvaci]

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

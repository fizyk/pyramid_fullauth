=======
CHANGES
=======

CURRENT
-------
- started test migration to py.test
- extracted UserEmailMixin from User model
- validation exception improvements

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

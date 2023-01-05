CHANGELOG
=========

.. towncrier release notes start

2.0.1 (2023-01-05)
==================

Miscellaneus
------------

- Deploy documentation to github pages and change package uri to the new place documentation is being published on. (`#638 <https://https://github.com/fizyk/pyramid_fullauth/issues/638>`_)


2.0.0 (2022-12-27)
==================

Breaking changes
----------------

- pyramid_fullauth no longer supports Authentication and Authorisation legacy policies. (`#636 <https://https://github.com/fizyk/pyramid_fullauth/issues/636>`_)


Features
--------

- Add Python 3.10 to the supported python versions (`#495 <https://https://github.com/fizyk/pyramid_fullauth/issues/495>`_)
- Support python 3.11 (`#621 <https://https://github.com/fizyk/pyramid_fullauth/issues/621>`_)
- Migrated pyramid_fullauth to the pyramid 2.0 Security policy from legacy authentication and authorization policies.

  You'll have to migrate as well when upgrading pyramid_fullauth. See more at `Upgrading Authentication/Authorization <https://docs.pylonsproject.org/projects/pyramid/en/latest/whatsnew-2.0.html#upgrading-authentication-authorization>`_ (`#636 <https://https://github.com/fizyk/pyramid_fullauth/issues/636>`_)


Miscellaneus
------------

- Dropped custom csrf check option. It wasn't tested internally,
  wasn't actually used for views, and overshadowed official pyramid's predicate,
  that was dropped in pyramid 2.0, and was deprecated since pyramid 1.7. (`#387 <https://https://github.com/fizyk/pyramid_fullauth/issues/387>`_)
- Removed UserEmailMixin.__pattern_mail which was unused. (`#436 <https://https://github.com/fizyk/pyramid_fullauth/issues/436>`_)
- Use towncrier to manage Changelog (`#619 <https://https://github.com/fizyk/pyramid_fullauth/issues/619>`_)
- Migrate development dependency management to pipenv (`#620 <https://https://github.com/fizyk/pyramid_fullauth/issues/620>`_)
- Add your info here (`#622 <https://https://github.com/fizyk/pyramid_fullauth/issues/622>`_)
- Use shared automerge action for merging dependabot PRs automatically.
  It's based on github actions. (`#623 <https://https://github.com/fizyk/pyramid_fullauth/issues/623>`_)
- Migrate version management tool to tbump (`#624 <https://https://github.com/fizyk/pyramid_fullauth/issues/624>`_)


1.0.1
----------

- [cleanup] Removed internal compat (pyramid_fullauth is now python 3 only)
- [cleanup] Removed references to pyramid.compat (pyramid_fullauth is now python 3 only)

1.0.0
----------

- [packaging] use setup.cfg to define package metadata nad options
- [cleanup] blackify codebase
- [enhancement] move CI to github-actions
- [breaking] removed dependency on tzf.pyramid_yml and pymlconf. All configuration has to be handled within .ini file now.
- [enhancement] refactored route_predicates. Now user_path_hash can handle all user hashes.
- [enhancement] Changed default cookie session factory from `UnencryptedCookieSessionFactoryConfig` to `SignedCookieSessionFactory`.
- [enhancement] Use require_csrf instead of use_csrf view decorator predicate.
  This raises now 400 http error instead of 401 in case of bad or no csrf token when required.
- [enhancement] Set default session serializer as JSONSerializer to comply with pyramid's 2.0 change
- [enhancement] Require minimum pyramid 1.10.
- [enhancement] properly lint code through pylint an fix found issues
- [security] Set minimum requirement for SQLAlchemy to be at least 1.3.0 to protect against
  `CVE-2019-7164 <https://nvd.nist.gov/vuln/detail/CVE-2019-7164>`_ and
  `CVE-2019-7548 <https://nvd.nist.gov/vuln/detail/CVE-2019-7548>`_

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

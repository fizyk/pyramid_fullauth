models
======

.. automodule:: pyramid_fullauth.models


    .. autoclass:: User
        :show-inheritance:
        :members:


    .. autoclass:: Group


    .. autoclass:: AuthenticationProvider


    models.mixins
    -------------

    .. automodule:: pyramid_fullauth.models.mixins


        .. autoclass:: UserPasswordMixin
            :members: check_password, hash_password, password_validator

            .. autoattribute:: password
            .. autoattribute:: _hash_algorithm
            .. autoattribute:: _salt
            .. autoattribute:: reset_key


        .. autoclass:: UserEmailMixin
            :members: validate_email, set_new_email, change_email

            .. autoattribute:: email
            .. autoattribute:: new_email
            .. autoattribute:: email_change_key


    models.extensions
    -----------------

    .. automodule:: pyramid_fullauth.models.extensions

        .. autoclass:: CaseInsensitive

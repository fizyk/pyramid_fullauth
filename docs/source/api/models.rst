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


        .. autoclass:: PasswordMixin
            :members: check_password, hash_password, password_validator

            .. autoattribute:: password
            .. autoattribute:: _hash_algorithm
            .. autoattribute:: _salt
            .. autoattribute:: reset_key



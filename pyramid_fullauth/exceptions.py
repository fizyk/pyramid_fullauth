# -*- coding: utf-8 -*-


class DeleteException(Exception):

    '''
        Exception risen when the user can't be deleted
    '''
    pass


class ValidateError(ValueError):

    '''
        Base of every validate error in pyramid_fullauth
    '''
    pass


class EmptyPasswordError(ValidateError):

    '''
        Thrown whenever user is trying to set empty password
    '''
    pass


class ShortPasswordError(ValidateError):

    '''
    Thrown when password doesn't meet the length requirement
    '''
    pass


class PasswordConfirmMismatchError(ValidateError):

    '''
        Thrown when there's a mismatch with cpassword_confirm
    '''
    pass

# -*- coding: utf-8 -*-


class DeleteException(Exception):

    '''
        Exception risen when the user can't be deleted
    '''
    pass


class EmptyPasswordError(ValueError):

    '''
        Thrown whenever user is trying to set empty password
    '''
    pass

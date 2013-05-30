# -*- coding: utf-8 -*-
import logging
from tzf.pyramid_yml import config_defaults

__version__ = '0.0.1a'


logger = logging.getLogger(__name__)


def includeme(configurator):
    '''
    pyramid_fullauth includeme method

    :param pyramid.configurator.Configurator configurator: pyramid's configurator object
    '''

    config_defaults(configurator, 'pyramid_fullauth:config')

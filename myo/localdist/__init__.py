# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.

import os
HERE = os.path.dirname(__file__)

from myo.platform import platform

def select():
    r""" Returns the path to the directory which contains the
    distributables for the current platform. """

    if platform == 'Windows':
        return os.path.join(HERE, 'win')
    elif platform == 'Darwin':
        return os.path.join(HERE, 'mac')
    else:
        raise EnvironmentError('no local distribution for %s' % platform)

dist_path = select()


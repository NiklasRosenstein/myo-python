# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.

from __future__ import absolute_import

import os
import platform as _platform

def select():
    platform = _platform.platform().split('-')[0]

    if platform.startswith('Windows'):
        return 'Windows'
    elif platform.startswith('Darwin'):
        return 'Darwin'
    else:
        raise EnvironmentError('unsupported platform %s' % platform)

platform = select()


# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.

from __future__ import absolute_import

import os
import sys
import platform as _platform

def select():
    arch = 'x64' if sys.maxsize > (2 ** 32) else 'x86'
    platform = _platform.platform().split('-')[0]

    if platform.startswith('Windows'):
        result = 'Windows'
    elif platform.startswith('Darwin'):
        result = 'Darwin'
    else:
        raise EnvironmentError('unsupported platform %s' % platform)

    return result, arch

platform, arch = select()


# Copyright (c) 2015  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
:mod:`myo.platform`
~~~~~~~~~~~~~~~~~~~

Detects the current platform and exposes it as :data:`platform` and
:data:`arch` members. :data:`arch` can be either ``'x64'`` or ``'x86'``
and :data:`platform` can be one of the following:

- ``'Windows'``
- ``'Windows (Cygwin)``
- ``'Darwin'``

If the platform is not supported, :class:`EnvironmentError` is raised
when the module is loaded.
"""

from __future__ import absolute_import

import os
import sys
import platform as _platform

def select():
    arch = 'x64' if sys.maxsize > (2 ** 32) else 'x86'
    platform = _platform.platform().split('-')[0].lower()

    if platform.startswith('windows'):
        result = 'Windows'
    elif platform.startswith('cygwin'):
        result = 'Windows (Cygwin)'
    elif platform.startswith('darwin'):
        result = 'Darwin'
    elif os.environ.get('READTHEDOCS') == 'True':
        print('@@@ myo.utils.platform: READTHEDOCS: allowing platform {0!r} for building'.format(platform))
        result = 'Linux'
    else:
        raise EnvironmentError('unsupported platform %s' % platform)

    return result, arch

platform, arch = select()

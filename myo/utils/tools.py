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
:mod:`myo.tools`
~~~~~~~~~~~~~~~~
"""

import six
import sys

class ShortcutAccess(object):
    r""" Wrapper for any kind of object to make the access to
    attributes easier. Prefixes all accssed attribute names with
    the string supplied upon construction. """

    __slots__ = ('_ShortcutAccess__x', '_ShortcutAccess__prefix')

    def __init__(self, x, prefix):
        super(ShortcutAccess, self).__init__()

        if not isinstance(prefix, six.string_types):
            raise TypeError('prefix must be string')

        super(ShortcutAccess, self).__setattr__('_ShortcutAccess__x', x)
        super(ShortcutAccess, self).__setattr__('_ShortcutAccess__prefix', prefix)

    def __getattr__(self, name):
        return getattr(self.__x, self.__prefix + name)

    def __setattr__(self, name, value):
        setattr(self.__x, self.__prefix + name, value)

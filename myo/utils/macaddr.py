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
:mod:`myo.macaddr`
~~~~~~~~~~~~~~~~~~

Provides an immutable :class:`MacAddress` class.
"""

import six


class MacAddress(object):
    r""" This class represents an immutable MAC address. """

    @staticmethod
    def int_to_string(x):
        r""" Converts *x* being an integral number to a string MAC
        address. Raises a ValueError if *x* is a negative number or
        exceeds the MAC address range. """

        if x > (16 ** 12 - 1):
            raise ValueError('value exceeds MAC address range')
        if x < 0:
            raise ValueError('value must not be negative')

        # todo: convert to the right byte order. the resulting
        # mac address is reversed on my machine compared to the
        # mac address displayed by the hello-myo SDK sample.
        # See issue #7

        string = ('%x' % x).rjust(12, '0')
        assert len(string) == 12

        result = ':'.join(''.join(pair) for pair in zip(*[iter(string)]*2))
        return result.upper()

    @staticmethod
    def string_to_int(s):
        r""" Converts *s* being a string MAC address to an integer
        version. Raises a ValueError if the string is not a valid
        MAC address. """

        s = s.replace(':', '')
        if len(s) != 12:
            raise ValueError('not a valid MAC address')

        try:
            return int(s, 16)
        except ValueError:
            return ValueError('not a valid MAC address')

    def __new__(cls, value):
        if isinstance(value, MacAddress):
            return value
        else:
            obj = object.__new__(cls)
            obj.__init__(value)
            return obj

    def __init__(self, value):
        super(MacAddress, self).__init__()

        if isinstance(value, six.string_types):
            value = MacAddress.string_to_int(value)
        elif not isinstance(value, (int, long)):
            message = 'expected string or int for MacAddress, got %s'
            raise TypeError(message % value.__class__.__name__)

        self._string = MacAddress.int_to_string(value)
        self._value = value

    def __str__(self):
        return self._string

    def __repr__(self):
        return '<MAC %s>' % self._string

    @property
    def strval(self):
        return self._string

    @property
    def intval(self):
        return self._value

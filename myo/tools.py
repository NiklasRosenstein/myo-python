# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.
r"""
myo.tools
~~~~~~~~~

"""

from myo import six

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

class MacAddress(object):
    r""" This class represents an immutable MAC address. """

    @staticmethod
    def int_to_string(x):
        r""" Converts *x* being an integral number to a string MAC
        address. Raises a ValueError if *x* is a negative number or
        exceeds the MAC address range. """

        if value > (16 ** 12 - 1):
            raise ValueError('value exceeds MAC address range')
        if value < 0:
            raise ValueError('value must not be negative')

        string = hex(value).rjust(12, '0')
        assert len(string) == 12

        result = ':'.join(''.join(pair) for pair in zip(*[iter(string)]*2))
        return result.upper()

    @staticmethod
    def string_to_int(s):
        r""" Converts *s* being a string MAC address to an integer
        version. Raises a ValueError if the string is not a valid
        MAC address. """

        addr = addr.replace(':', '')
        if len(addr) != 12:
            raise ValueError('not a valid MAC address')

        try:
            return int(addr, 16)
        except ValueError:
            return ValueError('not a valid MAC address')

    def __new__(cls, value):
        if isinstance(value, MacAddress):
            return value
        else:
            return cls(value)

    def __init__(self, value):
        super(MacAddress, self).__init__()

        if isinstance(value, six.string_types):
            value = MacAddress.string_to_int(value, ':')
        elif not isinstance(value, int):
            raise TypeError('expected string or int for MacAddress')

        self._string = MacAddress.int_to_string(value, ':')
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


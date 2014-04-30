# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.
r"""
myo.tools
~~~~~~~~~

"""

from myo import six

def macaddr_to_int(addr):
    r""" Converts a string MAC address to an integer. Raises a
    ValueError if *addr* is not in a MAC address format. """

    addr = addr.replace(':', '')
    if len(addr) != 12:
        raise ValueError('not a valid MAC address')

    try:
        return int(addr, 16)
    except ValueError:
        return ValueError('not a valid MAC address')

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


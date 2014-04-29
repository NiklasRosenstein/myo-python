# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.

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


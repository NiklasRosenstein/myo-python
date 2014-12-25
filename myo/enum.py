# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.
r"""
myo.enum - Enumeration type-base
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import ctypes
from myo import six

class NoSuchEnumerationValue(Exception):
    r""" Raised when an Enumeration object was attempted to be
    created from an integer value but there was no enumeration
    object for this value.

    Note that you can specify ``__fallback_value__`` on an
    Enumeration class to not let it raise an exception. """

    pass

class Data(object):
    r""" Small class that can be used to specify data on an
    enumeration that should not be converted and interpreted
    as an enumeration value. """

    def __init__(self, value):
        super(Data, self).__init__()
        self.value = value

class EnumerationMeta(type):
    r""" This is the meta class for the :class:`Enumeration`
    base class which handles the automatic conversion of integer
    values to instances of the Enumeration class. There are no
    other types allowed other than int or :class:`Data` which
    will be unpacked on the Enumeration class.

    If an ``__fallback__`` was defined on class-level as
    an integer, the :class:`Enumeration` constructor will not
    raise a :class:`NoSuchEnumerationValue` exception if the
    passed value did not match the enumeration values, but
    instead return that fallback value.

    This fallback is not taken into account when attempting
    to create a new Enumeration object by a string. """

    _values = None
    __fallback__ = None

    def __new__(cls, name, bases, data):

        # Unpack all Data objects and create a dictionary of
        # values that will be converted to instances of the
        # enumeration class later.
        enum_values = {}
        for key, value in data.items():
            # Unpack Data objects into the class.
            if isinstance(value, Data):
                data[key] = value.value

            # Integers will be enumeration values.
            elif isinstance(value, int):
                enum_values[key] = value

            # We don't accept anything else.
            elif not key.startswith('_'):
                message = 'Enumeration must consist of ints or Data objects ' \
                          'only, got %s for \'%s\''
                raise TypeError(message % (value.__class__.__name__, key))

        # Create the new class object and give it the dictionary
        # that will map the integral values to the instances.
        class_ = type.__new__(cls, name, bases, data)
        class_._values = {}

        # Iterate over all entries in the data entries and
        # convert integral values to instances of the enumeration
        # class.
        for key, value in enum_values.items():

            # Create the new object. We must not use the classes'
            # __new__() method as it resolves the object from the
            # existing values.
            obj = object.__new__(class_)
            object.__init__(obj)

            obj.value = value
            obj.name = key

            if key == '__fallback__':
                obj.name = '-invalid-'
            else:
                class_._values[value] = obj
            setattr(class_, key, obj)

        return class_

    def __iter__(self):
        r""" Iterator over value-sorted enumeration values. """

        values = list(self._values.values())
        values.sort(key=lambda x: x.value)
        return iter(values)

class Enumeration(six.with_metaclass(EnumerationMeta)):
    r""" This is the base class for listing enumerations. All
    components of the class that are integers will be automatically
    converted to instances of the Enumeration class. Creating new
    instances of the class will only work if the value is an existing
    enumeration value. """

    def __new__(cls, value, _allow_fallback=True):
        r""" Creates a new instance of the Enumeration. *value* must
        be the integral number of one of the existing enumerations.
        :class:`NoSuchEnumerationValue` is raised in any other case.

        If a fallback was defined, it is returned only if *value*
        is an integer, not if it is a string. """

        # Try to find the actual instance of the Enumeration class
        # for the integer value and return it if it is available.
        if isinstance(value, int):
            try:
                value = cls._values[value]
            except KeyError:

                # If a fallback value was specified, use it
                # instead of raising an exception.
                if _allow_fallback and cls.__fallback__ is not None:
                    return cls.__fallback__

                raise NoSuchEnumerationValue(cls.__name__, value)

        # Or by name?
        elif isinstance(value, six.string_types):
            try:
                new_value = getattr(cls, value)
                if type(new_value) != cls:
                    raise AttributeError
            except AttributeError:
                raise NoSuchEnumerationValue(cls.__name__, value)

            value = new_value

        # At this point, value must be an object of the Enumeration
        # class, otherwise an invalid value was passed.
        if type(value) == cls:
            return value

        raise TypeError('value must be %s or int' % cls.__name__)

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if type(other) == self.__class__:
            return other.value == self.value
        elif isinstance(other, six.string_types):
            return other == self.name
        return False

    def __ne__(self, other):
        return not (self == other)

    def __int__(self):
        return self.value

    def __str__(self):
        class_name = self.__class__.__name__
        return '<%s: %s>' % (class_name, self.name)

    def __repr__(self):
        class_name = self.__class__.__name__
        return '<%s: [%d] %s>' % (class_name, self.value, self.name)

    def __index__(self):
        return self.value

    # ctypes support

    @property
    def _as_parameter_(self):
        return ctypes.c_int(self.value)

    @Data
    @classmethod
    def from_param(cls, obj):
        if isinstance(obj, (int,) + (six.string_types,)):
            obj = cls(obj)
        if type(obj) != cls:
            c1 = cls.__name__
            c2 = obj.__class__.__name__
            raise TypeError('can not create %s from %s' % (c1, c2))

        return ctypes.c_int(obj.value)

Enumeration.Data = Data


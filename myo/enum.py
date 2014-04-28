# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.

import ctypes

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

class EnumerationMeta(type(ctypes.c_int)):
    r""" This is the meta class for the :class:`Enumeration`
    base class which handles the automatic conversion of integer
    values to instances of the Enumeration class. There are no
    other types allowed other than int or :class:`Data` which
    will be unpacked on the Enumeration class.

    If an ``__fallback__`` was defined on class-level as
    an integer, the :class:`Enumeration` constructor will not
    raise a :class:`NoSuchEnumerationValue` exception if the
    passed value did not match the enumeration values, but
    instead return that fallback value. """

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
            elif not key.startswith('__') and not key.endswith('__'):
                message = 'Enumeration must consist of ints or Data objects ' \
                          'only, got %s for \'%s\''
                raise TypeError(message % (value.__class__.__name__, key))

        # Create the new class object and give it the dictionary
        # that will map the integral values to the instances.
        class_ = type(ctypes.c_int).__new__(cls, name, bases, data)
        class_._values = {}

        # Iterate over all entries in the data entries and
        # convert integral values to instances of the enumeration
        # class.
        for key, value in enum_values.iteritems():

            # Create the new object. We must not use the classes'
            # __new__() method as it resolves the object from the
            # existing values.
            obj = ctypes.c_int.__new__(class_)
            ctypes.c_int.__init__(obj)

            obj.value = value
            obj.name = key

            if key == '__fallback__':
                obj.name = '-invalid-'
            else:
                class_._values[value] = obj
            setattr(class_, key, obj)

        return class_

class Enumeration(ctypes.c_int):
    r""" This is the base class for listing enumerations. All
    components of the class that are integers will be automatically
    converted to instances of the Enumeration class. Creating new
    instances of the class will only work if the value is an existing
    enumeration value. """

    __metaclass__ = EnumerationMeta

    def __new__(cls, value):
        r""" Creates a new instance of the Enumeration. *value* must
        be the integral number of one of the existing enumerations.
        :class:`NoSuchEnumerationValue` is raised in any other case. """

        # Try to find the actual instance of the Enumeration class
        # for the integer value and return it if it is available.
        if isinstance(value, int):
            try:
                value = cls._values[value]
            except KeyError:

                # If a fallback value was specified, use it
                # instead of raising an exception.
                if cls.__fallback__ is not None:
                    return cls.__fallback__

                raise NoSuchEnumerationValue(cls.__name__, value)

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
        return '<%s: [%d] %s>' % (class_name, self.name, self.value)

    def __index__(self):
        return self.value

Enumeration.Data = Data


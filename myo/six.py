"""Utilities for writing code that runs on Python 2 and 3"""

# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.
r"""
myo.six - minimalistic Python 2/3 compatibility layer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a minimalistic clone of the original *six* module
with focus on the Python 3 style.

.. seealso:: https://pypi.python.org/pypi/six
"""

import sys
PY2 = sys.version_info[0] < 3
PY3 = not PY2

if PY2:
    print('Using Python 2')
    string_types = (basestring,)

    range = xrange
    def print_(*args, **kwargs):
        r""" print(value, ..., sep=' ', end='\n', file=sys.stdout, flush=False)

        Prints the values to a stream, or to sys.stdout by default.
        Optional keyword arguments:
        file:  a file-like object (stream); defaults to the current sys.stdout.
        sep:   string inserted between values, default a space.
        end:   string appended after the last value, default a newline.
        flush: whether to forcibly flush the stream. """

        sep = kwargs.pop('sep', ' ')
        end = kwargs.pop('end', '\n')
        file_ = kwargs.pop('file', sys.stdout)
        flush = kwargs.pop('flush', False)

        for arg in args[:-1]:
            file_.write(str(arg))
            file_.write(str(sep))

        if args:
            file_.write(str(args[-1]))
        file_.write(str(end))
        if flush and hasattr(file_, 'flush'):
            file_.flush()
else:
    print('Using Python 3')
    string_types = (str, bytes)

    range = __builtins__['range']
    print_ = __builtins__['print']

def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})

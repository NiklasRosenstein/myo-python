# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.
r"""
myo.six - minimalistic Python 2/3 compatibility layer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. seealso:: https://pypi.python.org/simple/six
"""

import sys
PY2 = sys.version_info[0] < 3
PY3 = not PY2

if PY2:
    string_types = (basestring,)

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
            file_.write(str(args))
            file_.write(str(sep))

        if args:
            file_.write(str(args[-1]))
        file_.write(str(end))
        if flush and hasattr(file_, 'flush'):
            file_.flush()

else:
    string_types = (str, bytes)
    print_ = __builtins__['print']


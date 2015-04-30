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


class error(Exception):
    """
    Base class for errors and exceptions in the :mod`myo` library.
    """


class ResultError(error):
    """
    Raised if the result of an operation with the Myo library
    was anything but successful.

    .. seealso:: :class:`enums.Result`
    """

    def __init__(self, kind, message):
        super(ResultError, self).__init__()
        self.kind = kind
        self.message = message

    def __str__(self):
        return str((self.kind, self.message))


class InvalidOperation(error):
    """
    Raised if an invalid operation is performed, eg. if you attempt to
    read the firmware version in any event other than *paired* and
    *connect*.
    """

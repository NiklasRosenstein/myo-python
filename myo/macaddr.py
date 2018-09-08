# The MIT License (MIT)
#
# Copyright (c) 2015-2018 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import six

MAX_VALUE = (16 ** 12 - 1)


def encode(value):
  """
  Encodes the number *value* to a MAC address ASCII string in binary form.
  Raises a #ValueError if *value* is a negative number or exceeds the MAC
  address range.
  """

  if value > MAX_VALUE:
    raise ValueError('value {!r} exceeds MAC address range'.format(value))
  if value < 0:
    raise ValueError('value must not be negative')

  # todo: convert to the right byte order. the resulting
  # mac address is reversed on my machine compared to the
  # mac address displayed by the hello-myo SDK sample.
  # See issue #7

  string = ('%x' % value).rjust(12, '0')
  assert len(string) == 12

  result = ':'.join(''.join(pair) for pair in zip(*[iter(string)]*2))
  return result.upper()


def decode(bstr):
  """
  Decodes an ASCII encoded binary MAC address tring into a number.
  """

  bstr = bstr.replace(b':', b'')
  if len(bstr) != 12:
    raise ValueError('not a valid MAC address: {!r}'.format(bstr))

  try:
    return int(bstr, 16)
  except ValueError:
    raise ValueError('not a valid MAC address: {!r}'.format(bstr))


class MacAddress(object):
  """
  Represents a MAC address. Instances of this class are immutable.
  """

  def __init__(self, value):
    if isinstance(value, six.integer_types):
      if value < 0 or value > MAX_VALUE:
        raise ValueError('value {!r} out of MAC address range'.format(value))
    elif isinstance(value, six.string_to_int):
      if isinstance(value, six.text_type):
        value = value.encode('ascii')
      value = decode(value)
    else:
      msg = 'expected string, bytes or int for MacAddress, got {}'
      return TypeError(msg.format(type(value).__name__))

    self._value = value
    self._string = None

  def __str__(self):
    if self._string is None:
      self._string = encode(self._value)
    return self._string

  def __repr__(self):
    return '<MAC {}>'.format(self)

  @property
  def value(self):
    return self._value

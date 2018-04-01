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


import time


class TimeInterval(object):
  """
  A helper class to keep track of a time interval.
  """

  def __init__(self, value, value_on_reset=None):
    self.value = value
    self.value_on_reset = value_on_reset
    self.start = time.clock()

  def check(self):
    """
    Returns #True if the time interval has passed.
    """

    if self.value is None:
      return True
    return (time.clock() - self.start) >= self.value

  def reset(self, value=None):
    """
    Resets the start time of the interval to now or the specified value.
    """

    if value is None:
      value = time.clock()
    self.start = value
    if self.value_on_reset:
      self.value = self.value_on_reset

  def check_and_reset(self, value=None):
    """
    Combination of #check() and #reset().
    """

    if self.check():
      self.reset(value)
      return True
    return False


class TimeoutManager(TimeInterval):

  def check(self):
    """
    Returns #True if the timeout is exceeded.
    """

    if self.value is None:
      return False
    return (time.clock() - self.start) >= self.value

  def remainder(self, max_value=None):
    """
    Returns the time remaining for the timeout, or *max_value* if that
    remainder is larger.
    """

    if self.value is None:
      return max_value
    remainder = self.value - (time.clock() - self.start)
    if remainder < 0.0:
      return 0.0
    elif max_value is not None and remainder > max_value:
      return max_value
    else:
      return remainder

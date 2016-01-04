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
"""
:mod:`myo.threading`
~~~~~~~~~~~~~~~~~~~~
"""

import time


class TimeoutClock(object):
    """
    This is a utility class to compute the time that should be passed
    to a Condition variable that could be notified before the timeout
    exceeded and before the actual data is available.

    If *timeout* is None, the *TimeoutClock* will always return False
    when retrieving :attr:`exceeded`.

    .. code-block:: python

        timer = TimeoutClock(timeout)
        with condition:
            while not timer.exceeded and not data_is_available():
                condition.wait(timer.remaining)
            if data_is_available():
                return get_data()
            else:
                # timeout exceeded
    """

    def __init__(self, timeout):
        super(TimeoutClock, self).__init__()
        self.timeout = timeout
        self.start_time = time.time()

    @property
    def passed(self):
        """
        Returns the time passed since the creation of the timer.
        This always functions, even if the *TimeoutClock* was
        initialized with None.
        """

        return time.time() - self.start_time

    @property
    def exceeded(self):
        """
        Returns True if the timeout is exceeded, False if not. Will
        always return False if the *TimeoutClock* was initialized with
        None.
        """

        if self.timeout is None:
            return False
        return self.passed >= self.timeout

    @property
    def remaining(self):
        """
        Returns the time that is remaining to be waited that should be
        passed to the Condition variables ``wait()`` method in the loop.
        Returns None if the *TimeoutClock* was initialized with None.
        """

        if self.timeout is None:
            return None
        return self.timeout - self.passed

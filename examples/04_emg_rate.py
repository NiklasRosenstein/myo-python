# The MIT License (MIT)
#
# Copyright (c) 2017 Niklas Rosenstein
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

from __future__ import print_function
import collections
import myo
import time
import sys


class EmgRate(myo.DeviceListener):

  def __init__(self, n):
    super(EmgRate, self).__init__()
    self.times = collections.deque()
    self.last_time = None
    self.n = int(n)

  @property
  def rate(self):
    if not self.times:
      return 0.0
    else:
      return 1.0 / (sum(self.times) / float(self.n))

  def on_arm_synced(self, event):
    event.device.stream_emg(True)

  def on_emg(self, event):
    t = time.clock()
    if self.last_time is not None:
      self.times.append(t - self.last_time)
      if len(self.times) > self.n:
        self.times.popleft()
    self.last_time = t


def main():
  myo.init()
  hub = myo.Hub()
  listener = EmgRate(n=50)
  while hub.run(listener.on_event, 500):
    print("\r\033[KEMG Rate:", listener.rate, end='')
    sys.stdout.flush()


if __name__ == '__main__':
  main()

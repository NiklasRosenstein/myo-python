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
"""
This simple example demonstrates how to implement a Device Listener and
how to stop the event flow when the double tap pose is recognized.
"""

from __future__ import print_function
import myo


class Listener(myo.DeviceListener):

  def on_connected(self, event):
    print("Hello, '{}'! Double tap to exit.".format(event.device_name))
    event.device.vibrate(myo.VibrationType.short)
    event.device.request_battery_level()

  def on_battery_level(self, event):
    print("Your battery level is:", event.battery_level)

  def on_pose(self, event):
    if event.pose == myo.Pose.double_tap:
      return False


if __name__ == '__main__':
  myo.init()
  hub = myo.Hub()
  listener = Listener()
  while hub.run(listener.on_event, 500):
    pass
  print('Bye, bye!')

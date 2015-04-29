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

from __future__ import print_function

import myo
import random

from myo.lowlevel import pose_t, stream_emg

myo.init()

SHOW_OUTPUT_CHANCE = 0.01
r"""
There can be a lot of output from certain data like acceleration and orientation.
This parameter controls the percent of times that data is shown.
"""

class Listener(myo.DeviceListener):
    # return False from any method to stop the Hub

    def on_connect(self, myo, timestamp):
        print("Connected to Myo")
        myo.vibrate('short')
        myo.request_rssi()

    def on_rssi(self, myo, timestamp, rssi):
        print("RSSI:", rssi)

    def on_event(self, event):
        r""" Called before any of the event callbacks. """

    def on_event_finished(self, event):
        r""" Called after the respective event callbacks have been
        invoked. This method is *always* triggered, even if one of
        the callbacks requested the stop of the Hub. """

    def on_pair(self, myo, timestamp):
        print('Paired')
        print("If you don't see any responses to your movements, try re-running the program or making sure the Myo works with Myo Connect (from Thalmic Labs).")
        print("Double tap enables EMG.")
        print("Spreading fingers disables EMG.\n")

    def on_disconnect(self, myo, timestamp):
        print('on_disconnect')

    def on_pose(self, myo, timestamp, pose):
        print('on_pose', pose)
        if pose == pose_t.double_tap:
            print("Enabling EMG")
            print("Spreading fingers disables EMG.")
            print("=" * 80)
            myo.set_stream_emg(stream_emg.enabled)
        elif pose == pose_t.fingers_spread:
            print("=" * 80)
            print("Disabling EMG")
            myo.set_stream_emg(stream_emg.disabled)

    def on_orientation_data(self, myo, timestamp, orientation):
        show_output('orientation', orientation)

    def on_accelerometor_data(self, myo, timestamp, acceleration):
        show_output('acceleration', acceleration)

    def on_gyroscope_data(self, myo, timestamp, gyroscope):
        show_output('gyroscope', gyroscope)

    def on_unlock(self, myo, timestamp):
        print('unlocked')

    def on_lock(self, myo, timestamp):
        print('locked')

    def on_sync(self, myo, timestamp, arm, x_direction):
        print('synced', arm, x_direction)

    def on_unsync(self, myo, timestamp):
        print('unsynced')

    def on_emg(self, myo, timestamp, emg):
        show_output('emg', emg)

def show_output(message, data):
    if random.random() < SHOW_OUTPUT_CHANCE:
        print(message + ':' + str(data))

def main():
    hub = myo.Hub()
    hub.set_locking_policy(myo.locking_policy.none)
    hub.run(1000, Listener())

    # Listen to keyboard interrupts and stop the
    # hub in that case.
    try:
        while hub.running:
            myo.time.sleep(0.2)
    except KeyboardInterrupt:
        print("Quitting ...")
        hub.stop(True)

if __name__ == '__main__':
    main()


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
import myo as libmyo; libmyo.init()
import time

def main():
    try:
        hub = libmyo.Hub()
    except MemoryError:
        print("Myo Hub could not be created. Make sure Myo Connect is running.")
        return

    feed = libmyo.device_listener.Feed()
    hub.run(1000, feed)
    try:
        print("Waiting for a Myo to connect ...")
        myo = feed.wait_for_single_device(2)
        if not myo:
            print("No Myo connected after 2 seconds.")
            return

        print("Hello, Myo! Requesting RSSI ...")
        myo.request_rssi()
        while hub.running and myo.connected and not myo.rssi:
            print("Waiting for RRSI...")
            time.sleep(0.001)
        print("RSSI:", myo.rssi)
        print("Goodbye, Myo!")
    except KeyboardInterrupt:
        print("Keyboard Interrupt.")
    else:
        print("Myo disconnected.")
    finally:
        print("Shutting down Myo Hub ...")
        hub.shutdown()

if __name__ == "__main__":
    main()

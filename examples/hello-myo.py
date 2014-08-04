# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.

import myo
import sys
myo.init()

from myo.six import print_

class Listener(myo.DeviceListener):
    #return False from any method to stop the Hub

    def on_connect(self, myo, timestamp):
        print 'on_connect'
        #print_("Hello Myo", myo.mac_address)
        myo.request_rssi()

    def on_rssi(self, myo, timestamp, rssi):
        print_("RSSI:", rssi)

    def on_event(self, event):
        r""" Called before any of the event callbacks. """

    def on_event_finished(self, event):
        print 'on_event_finished'
        r""" Called after the respective event callbacks have been
        invoked. This method is *always* triggered, even if one of
        the callbacks requested the stop of the Hub. """

    def on_pair(self, myo, timestamp):
        print 'on_pair'

    def on_disconnect(self, myo, timestamp):
        print 'on_disconnect'

    def on_pose(self, myo, timestamp, pose):
        print 'on_pose', pose

    def on_orientation_data(self, myo, timestamp, orientation):
        print 'on_orientation_data'

    def on_accelerometor_data(self, myo, timestamp, acceleration):
        print 'on_accelerometor_data'

    def on_gyroscope_data(self, myo, timestamp, gyroscope):
        print 'on_gyroscope_data'

def main():
    try:
        hub = myo.Hub()
        hub.run(1000, Listener())
        #hub.pair_any()
    except:
        sys.stderr.write('Make sure that Myo Connect is running and a Myo is paired.\n')
        raise

    # Listen to keyboard interrupts and stop the
    # hub in that case.
    try:
        while hub.running:
            myo.time.sleep(0.2)
    except KeyboardInterrupt:
        print_("Quitting ...")
        hub.stop(True)

if __name__ == '__main__':
    main()


# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.

import myo
myo.init()

from myo.six import print_

class Listener(myo.DeviceListener):

    def on_pair(self, myo, timestamp):
        print_("Hello Myo", myo.mac_address)
        myo.request_rssi()

    def on_rssi(self, myo, timestamp, rssi):
        print_("RSSI:", rssi)
        return False # Stop the Hub

def main():
    hub = myo.Hub()
    hub.async_until_stopped(1000, Listener())
    hub.pair_any()
    hub.join()

if __name__ == '__main__':
    main()


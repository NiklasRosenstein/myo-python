# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.

import myo
myo.init()

from myo.six import print_

class Listener(myo.DeviceListener):

    def on_connect(self, myo, timestamp):
        print_("Connected to Myo")
        myo.vibrate('short')
        myo.training_load_profile()

    def on_pose(self, myo, timestamp, pose):
        if pose != 'none':
            print_("You just made the", pose.name, "pose!")

def main():
    hub = myo.Hub()
    hub.run(1000, Listener())
    hub.pair_any()

    # Listen to keyboard interrupts and stop the
    # hub in that case.
    try:
        while hub.running:
            myo.time.sleep(0.2)
    except KeyboardInterrupt:
        print_("Quitting ...")
        hub.stop()
    hub.join()

if __name__ == '__main__':
    main()


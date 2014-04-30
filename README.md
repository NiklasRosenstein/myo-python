# Python bindings for the Myo SDK

The Python `myo` package is a ctypes based wrapper for the Myo shared
libraries. Its goal is to give a complete exposure of the Myo SDK as a
separate Highlevel and Lowlevel API to Python developers. 

## Compatibility

This package is compatible with Python 2 and 3. Development is taking
place with CPython 2.7 and 3.4.

## Example

```python
# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.

import time
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
    listener = Listener()
    hub = myo.Hub()
    hub.asnyc_till_stopped(1000, listener)
    hub.pair_any()

    try:
        while hub.running:
            time.sleep(0.2)
    except KeyboardInterrupt:
        hub.stop()
    hub.join()

if __name__ == '__main__':
    main()
```

----

__Copyright (C) 2014  Niklas Rosenstein__, All rights reserved.


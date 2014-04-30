# Python bindings for the Myo SDK

The Python `myo` package is a ctypes based wrapper for the Myo shared
libraries. Its goal is to give a complete exposure of the Myo SDK as a
Highlevel API to Python developers.

Python Myo is compatible with Python 2 and 3!

## Example

```python
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
```

----

__Copyright (C) 2014  Niklas Rosenstein__,
All rights reserved.


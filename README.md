# Python bindings for the Myo SDK

The Python `myo` package is a ctypes based wrapper for the Myo shared
libraries. Its goal is to give a complete exposure of the Myo SDK as a
Highlevel API to Python developers.

Python Myo is compatible with Python 2 (master branch) and 3 (using the [python3 branch](https://github.com/juharris/myo-python/tree/python3)) !

We'll work on a way to get master working with both Python 2 and 3 but for now the [python3 branch](https://github.com/juharris/myo-python/tree/python3) will also be maintained.

## Example

```python
# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.

import myo
myo.init()

from myo.six import print_

class Listener(myo.DeviceListener):

    def on_pair(self, myo, timestamp):
        print_("Hello Myo")

    def on_rssi(self, myo, timestamp, rssi):
        print_("RSSI:", rssi)
        return False # Stop the Hub

def main():
    hub = myo.Hub()
    hub.set_locking_policy(myo.locking_policy.none)
    hub.run(1000, Listener())

if __name__ == '__main__':
    main()
```

See [hello_myo.py](examples/hello_myo.py) for more examples.

----

__Copyright (C) 2014  Niklas Rosenstein__,
All rights reserved.


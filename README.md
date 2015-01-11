# Python bindings for the Myo SDK

The Python `myo` package is a ctypes based wrapper for the Myo shared libraries.
Its goal is to give a complete exposure of the Myo SDK as a high level API to Python developers.

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

## Getting Started
0. Add this folder (the folder containing README.md and myo/) to your `PYTHONPATH`.
  * command line: `export PYTHONPATH=$PYTHONPATH:/path/to/myo-python`; or
  * programmatically in your Python module:
  ```python
  import os, sys
  sys.path.append(os.path.join('path', 'to', 'myo-python'))
  ```
0. Download the Myo SDK for your system from [here](https://developer.thalmic.com/downloads).
0. Add the Myo SDK to your path.
  * Windows: Add the **full absolute path** of the folder containing myo32.dll and myo64.dll (for example "C:\Program Files\Thalmic Labs\myo-sdk-win-0.8.0\bin" without quotes) to your `PATH`.
  * Mac: Add the **full absolute path** for myo.framework/ (for example "/Library/frameworks/myo.framework" without quotes) to `DYLD_LIBRARY_PATH`. Comment on [#10](https://github.com/juharris/myo-python/issues/10) if you have issues.
  * Linux: Use Unity? Comment on [#11](https://github.com/juharris/myo-python/issues/11) if you figure this out and we'll update the README. People have definitely gotten the Myo SDK to work on Linux and there should be some forum posts about it somewhere.

----

__Copyright (C) 2014  Niklas Rosenstein__,
All rights reserved.


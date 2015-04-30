# Python bindings for the Myo SDK

The Python `myo` package is a ctypes based wrapper for the Myo shared
libraries provided by Thalmic Labs. The aim is to provide a complete Python
interface for the Myo SDK as a high level API to Python developers.

The myo-python package is compatible with Python 2 and 3.

```python
from __future__ import print_function
import myo
myo.init()

class Listener(myo.DeviceListener):

    def on_pair(self, myo, timestamp):
        print("Hello Myo")

    def on_rssi(self, myo, timestamp, rssi):
        print("RSSI:", rssi)
        return False # Stop the Hub

def main():
    hub = myo.Hub()
    hub.set_locking_policy(myo.locking_policy.none)
    hub.run(1000, Listener())

if __name__ == '__main__':
    main()
```

Check the [examples](examples/) directory for more.

## Requirements

- [six](https://pypi.python.org/pypi/six) for Python 2 and 3 compatibility

## Getting Started

1. Download myo-python or clone it from GitHub
2. Install it, for testing with `pip install -e myo-python/` or add
   it to your `PYTHONPATH`
3. Make sure myo-python can find the Myo SDK binaries by adding it to
   `PATH` either outside or inside your Python application/script

You can download the Myo SDK from [here](https://developer.thalmic.com/downloads).

### Windows (Cygwin)

    $ git clone git@github.com:NiklasRosenstein/myo-python
    $ virtualenv env --no-site-packages
    $ source env/bin/activate
    $ pip install -e myo-python
    $ export PATH=$PATH:$(pwd)/myo-sdk-win-0.8.1/bin
    $ python3 myo-python/examples/hello_myo.py

### Mac

    $ git clone git@github.com:NiklasRosenstein/myo-python
    $ virtualenv env --no-site-packages
    $ source env/bin/activate
    $ pip install -e myo-python
    $ export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:$(pwd)/myo-sdk-mac-0.8.1/myo.framework
    $ python3 myo-python/examples/hello_myo.py

------------------------------------------------------------------------

This project is licensed under the MIT License. Copyright &copy; 2015 Niklas Rosenstein

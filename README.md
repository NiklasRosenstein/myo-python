# Python bindings for the Myo SDK

*Version 0.2.0-dev*

The Python `myo` package is a ctypes based wrapper for the Myo shared
libraries provided by Thalmic Labs. The aim is to provide a complete Python
interface for the Myo SDK as a high level API to Python developers.

The myo-python package is compatible with Python 2 and 3.

> **Note**: This branch contains the new development of `myo-v0.2.0`
> which might loose backwards compatibility soon. Check the `v0.1.0`
> branch for the older version.

```python
from __future__ import print_function
import myo as libmyo; libmyo.init()

class Listener(libmyo.DeviceListener):

    def on_pair(self, myo, timestamp):
        print("Hello Myo")

    def on_rssi(self, myo, timestamp, rssi):
        print("RSSI:", rssi)
        return False # Stop the Hub

def main():
    hub = libmyo.Hub()
    hub.set_locking_policy(libmyo.LockingPolicy.none)
    hub.run(1000, Listener())

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Goodbye")
    finally:
        hub.stop(True)
    hub.shutdown()


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

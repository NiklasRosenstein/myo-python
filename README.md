# Python bindings for the Myo SDK

The Python `myo` package is a ctypes based wrapper for the Myo shared libraries provided by Thalmic Labs. The aim is to provide a complete Python interface for the Myo SDK as a high level API to developers using Pytho 2 or 3.

There are two ways you can use the Myo bindings, by polling data or by getting push notifications. Basically, your way to start and end a connection with Myo(s) is like this:

```python
import myo as libmyo; libmyo.init()

hub = libmyo.Hub()
hub.run(1000, listener)
try:
    # Wait until something happens or the hub is shut down.
    while hub.running:
        time.sleep(0.25)
finally:
    hub.shutdown()
```

> *Note*: It is very important that you wrap everything in a try-finally clause to be able to shut down the hub when you want to exit the application as the Hub starts a non-daemon thread. Also, if the hub is garbage collected without it being `shutdown()`, a warning will be printed.

By the way, we prefer to import the `myo` package as `libmyo` as it is very likely you will have a `myo` variable in your local scope that represents a single armband.

## Pushing

You must implement the `myo.device_listener.DeviceListener` class and pass an instance of it to `myo.Hub.run()`. Any event that is sent via the Myo will end up in your listener.

Generally, implementing a `DeviceListener` should be preferred if it will not involve any more complexities in your application.

```python
class Listener(libmyo.DeviceListener):

    def on_pair(self, myo, timestamp):
        print("Hello, Myo!")

    def on_unpair(self, myo, timestamp):
        print("Goodbye, Myo!")

    def on_orientation_data(self, myo, timestamp, quat):
        print("Orientation:", quat.x, quat.y, quat.z, quat.w)
```

## Pulling

Pulling can be done by using an instance of `myo.device_listener.Feed` as the listener to `Hub.run()`. The Feed will cache any data when its received and it can be accessed through a MyoProxy object at any time.

```python
feed = libmyo.device_listener.Feed()
hub.run(1000, feed)
try:
    myo = feed.wait_for_single_device(timeout=10)
    if not myo:
        print("No Myo connected after 10 seconds.")
        return

    print("Hello, Myo!")
    while hub.running and myo.connected:
        quat = myo.orientation
        print("Orientation:", quat.x, quat.y, quat.z, quat.w)
    print("Goodbye, Myo!")
finally:
    hub.shutdown()
```

Check the [examples](examples/) directory for more.

## Requirements

- [six](https://pypi.python.org/pypi/six) for Python 2 and 3 compatibility

## Getting Started

1. Download myo-python or clone it from GitHub
2. Install it, for testing with `pip install -e myo-python/` or add it to your `PYTHONPATH`
3. Make sure myo-python can find the Myo SDK binaries by adding it to `PATH` either outside or inside your Python application/script

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

For a list of all contributors, see [here](https://github.com/NiklasRosenstein/myo-python/graphs/contributors).

------------------------------------------------------------------------

This project is licensed under the MIT License. Copyright &copy; 2015 Niklas Rosenstein

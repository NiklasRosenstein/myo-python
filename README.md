<p align="center">
  <img align="center" src="https://www.myo.com/assets/sapphire/navbar/myo-logo.svg"/>
  <img align="center" src="https://www.python.org/static/community_logos/python-logo.png"/>
</p>
<p align="center">
  <a href="https://opensource.org/licenses/MIT" alt="License: MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square"/>
  </a>
</p>
<h1 align="center">Python bindings for the Myo SDK</h1>

Myo-Python is a [CFFI] wrapper for the [Thalmic Myo SDK].

__Table of Contents__

* [Documentation](#documentation)
* [Example](#example)
* [Migrating from v0.2.x](#migrating-from-v0.2.x)
* [Projects using Myo-Python](#projects-using-myo-python)

[CFFI]: https://pypi.python.org/pypi/cffi
[Thalmic Myo SDK]: https://developer.thalmic.com/downloads

### Documentation

The documentation can currently be found in the `docs/` directory in the
[GitHub Repository](https://github.com/NiklasRosenstein/myo-python).

### Example

Myo-Python mirrors the usage of the Myo C++ SDK in many ways as it also
requires you to implement a `DeviceListener` that will then be invoked for
any events received from a Myo device.

```python
import myo

class Listener(myo.DeviceListener):
  def on_paired(self, event):
    print("Hello, {}!".format(event.device_name))
    event.device.vibrate(myo.VibrationType.short)
  def on_unpaired(self, event):
    return False  # Stop the hub
  def on_orientation(self, event):
    orientation = event.orientation
    acceleration = event.acceleration
    gyroscope = event.gyroscope
    # ... do something with that

if __name__ == '__main__':
  myo.init(sdk_path='./myo-sdk-win-0.9.0/')
  hub = myo.Hub()
  listener = Listener()
  while hub.run(listener.on_event, 500):
    pass
```

As an alternative to implementing a custom device listener, you can instead
use the `myp.ApiDeviceListener` class which allows you to read the most recent
state of one or multiple Myo devices.

```python
import myo
import time

def main():
  myo.init(sdk_path='./myo-sdk-win-0.9.0/')
  hub = myo.Hub()
  listener = myo.ApiDeviceListener()
  with hub.run_in_background(listener.on_event):
    print("Waiting for a Myo to connect ...")
    device = listener.wait_for_single_device(2)
    if not device:
      print("No Myo connected after 2 seconds.")
      return
    print("Hello, Myo! Requesting RSSI ...")
    device.request_rssi()
    while hub.running and device.connected and not device.rssi:
      print("Waiting for RRSI...")
      time.sleep(0.001)
    print("RSSI:", device.rssi)
    print("Goodbye, Myo!")
```

### Migrating from v0.2.x

The v0.2.x series of the Myo-Python library used `ctypes` and has a little
bit different API. The most important changes are:

* The `Hub` object no longer needs to be shut down explicitly
* The `DeviceListener` method names changed to match the exact event name
  as specified by the Myo SDK (eg. from `on_pair()` to `on_paired()`)
* The `myo.init()` function provides a few more parameters to control the
  way `libmyo` is detected.
* `myo.Feed` has been renamed to `myo.ApiDeviceListener`

### Projects using Myo-Python

- [Myo Matlab](https://github.com/yijuilee/myomatlab)

### Changes

#### v1.0.3 (2018-06-28)

- `Event.mac_address` now returns `None` if the event's type is `EventType.emg` (#62)
- `Hub.run()` now accepts `DeviceListener` objects for its *handler* parameter.
  This carries over to `Hub.run_forever()` and `Hub.run_in_background()`.
- Replace requirement `nr>=2.0.10,<3` in favor of `nr.types>=1.0.3`

#### v1.0.2 (2018-06-09)

- Fix `Event.warmup_result` (PR #58 @fribeiro1)

#### v1.0.1 (2018-06-09)

- Fix `Event.rotation_on_arm` (#59)

#### v1.0.0 (2018-06-03)

- Rewrite using CFFI

----

<p align="center">This project is licensed under the MIT License.</br>
Copyright &copy; 2015-2018 Niklas Rosenstein</p>

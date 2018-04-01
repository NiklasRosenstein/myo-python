<p align="center">
  <img align="center" src="https://www.myo.com/assets/sapphire/navbar/myo-logo.svg"/>
  <img align="center" src="https://www.python.org/static/community_logos/python-logo.png"/>
</p>
<p align="center">
  <a href="https://opensource.org/licenses/MIT" alt="License: MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square"/>
  </a>
  <img src="https://img.shields.io/badge/version-1.0.0--dev-blue.svg?style=flat-square"/>
  <a href="http://myo-python.readthedocs.org/en/latest/?badge=latest" alt="Documentation Status">
    <img src="https://readthedocs.org/projects/myo-python/badge/?version=latest"/>
  </a>
</p>
<h1 align="center">Python bindings for the Myo SDK</h1>

This library is Python 2 and 3 compatible a [CFFI] based wrapper around the
[Thalmic Myo SDK]. The documentation can be found [here][Documentation].

  [CFFI]: https://pypi.python.org/pypi/cffi
  [Thalmic Myo SDK]: https://developer.thalmic.com/downloads
  [Documentation]: http://myo-python.readthedocs.org/en/latest/index.html

### Example

To receive data from a Myo device, you need to implement a `myo.DeviceListener`.
Alternatively, you can use the `myo.ApiDeviceListener` that allows you to read
the last state of a property without being bound to the event flow.

Below is an example that implements a `myo.DeviceListener`:

```python
import myo

class Listener(myo.DeviceListener):

  def on_paired(self, event):
    print("Hello, {}!".format(event.device_name))
    event.device.vibrate(myo.VibrationType.short)

  def on_unpair(self, event):
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

### Projects that use myo-python

- [Myo Matlab](https://github.com/yijuilee/myomatlab)

----

<p align="center">This project is licensed under the MIT License.</br>
Copyright &copy; 2015-2018 Niklas Rosenstein</p>

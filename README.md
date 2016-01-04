# Python bindings for the Myo SDK

[![Documentation Status](https://readthedocs.org/projects/myo-python/badge/?version=latest)](http://myo-python.readthedocs.org/en/latest/?badge=latest)

This module is a ctypes based wrapper for the Thalmic Myo SDK that is
compatible with Python 2 and 3. Check out the [docs][] for a tutorial
and the API documentation and the [examples](examples) folder.

__Features__

- [x] Python 2 & 3 compatible
- [x] Math classes for Vector and Quaternion

__Example__

```python
from time import sleep
from myo import init, Hub, DeviceListener

class Listener(DeviceListener):

    def on_pair(self, myo, timestamp, firmware_version):
        print("Hello, Myo!")

    def on_unpair(self, myo, timestamp):
        print("Goodbye, Myo!")

    def on_orientation_data(self, myo, timestamp, quat):
        print("Orientation:", quat.x, quat.y, quat.z, quat.w)

init()
hub = Hub()
hub.run(1000, Listener())
try:
    while True:
        sleep(0.5)
except KeyboardInterrupt:
    print('\nQuit')
finally:
    hub.shutdown()  # !! crucial
```

__Projects that use myo-python__

- [Myo Matlab](https://github.com/yijuilee/myomatlab)

  [docs]: http://myo-python.readthedocs.org/en/latest/index.html

----

<p align="center">This project is licensed under the MIT License.</br>
Copyright &copy; 2015 Niklas Rosenstein</p>

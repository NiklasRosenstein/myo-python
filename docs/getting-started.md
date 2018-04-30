+++
title = "Getting Started"
ordering = 1
+++

Make sure you follow the installation instructions on the main page, first.

To receive data from a Myo device, you need to implement a `myo.DeviceListener`.
Alternatively, you can use the `myo.ApiDeviceListener` that allows you to read
the last state of a property without being bound to the event flow.

## Custom DeviceListener

Below is an example that implements a `myo.DeviceListener`:

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

## Using ApiDeviceListener

Using the stateful `myo.ApiDeviceListener` can make development a lot easier
in some cases as you are not restricted to the Myo event flow.

```python
import myo
import time

def main():
  myo.init()
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

if __name__ == "__main__":
  main()
```

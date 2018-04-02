+++
title = "API Documentation"
ordering = 4
+++

## Data Members

### `myo.supported_sdk_version`

The SDK version that the `myo` Python library supports. This is currently set
to the string `"0.9.0"`.

## Functions

### `myo.init(lib_name=None, bin_path=None, sdk_path=None)`

Load the Myo shared library. This must be called before using any other
functionality of the library that interacts with the Myo SDK.

## Device Listeners

### `myo.DeviceListener` Class

The base class for implementing a device listener that will receive events
from Myo Connect. Pass the `on_event` method to `Hub.run()`. The default
implementation of `on_event()` method will redirect the event to the
respective handler function based on the event type.

* `on_paired(event)`
* `on_unpaired(event)`
* `on_connected(event)`
* `on_disconnected(event)`
* `on_arm_synced(event)`
* `on_arm_unsynced(event)`
* `on_unlocked(event)`
* `on_locked(event)`
* `on_pose(event)`
* `on_orientation(event)`
* `on_rssi(event)`
* `on_battery_level(event)`
* `on_emg(event)`
* `on_warmup_complete(event)`

### `myo.ApiDeviceListener`

This device listener implementation records any data it receives per device.

#### `.wait_for_single_device(timeout=None, interval=0.5)`

Waits until a Myo is paired and connected and returns its `DeviceProxy`.
If no Myo connects until *timeout* runs out, `None` is returned.

#### `.devices`

A list of `DeviceProxy` objects that are paired.

#### `.connected_devices`

A list of `DeviceProxy` objects that are connected. This is a subset of
`.devices`.

## Classes

### `myo.Hub` Class

The hub is responsible for invoking your `DeviceListener`. The hub can be
run synchronously or in the background. Note that with the background way,
as soon as the end of the context-manager is reached, the hub will stop.

```python
hub = myo.Hub()
listener = MyListener()

# Synchronous -- manual polling.
while hub.run(listener.on_event, duration_ms=500):
  # Can do something after every run.
  pass

# Synchronous.
hub.run_forever(listener.on_event)

# Asynchrnous.
with hub.run_in_background(listener.on_event):
  # Do stuff while your listener is invoked in the background.
  # Note that reaching the end of the with block ends the hub.
```

#### `.locking_policy`

#### `.running`

#### `.run(handler, duration_ms)`

#### `.run_forever(handler, duration_ms=500)`

#### `.run_in_background(handler, duration_ms=500)`

#### `.stop()`

### `myo.Device` Class

Represents a Myo device.

#### `.vibrate(type=VibrationType.medium)`

#### `.stream_emg(type)`

#### `.request_rssi()`

#### `.request_battery_level()`

#### `.unlock(type=UnlockType.hold)`

#### `.lock()`

#### `.notify_user_action(type=UserActionType.single)`

### `myo.Event` Class

#### `.type`

#### `.timestamp`

#### `.device`

#### `.device_name`

#### `.mac_address`

#### `.firmware_version`

#### `.arm`

#### `.x_direction`

#### `.warmup_state`

#### `.warmup_result`

#### `.rotation_on_arm`

#### `.orientation`

#### `.acceleration`

#### `.gyroscope`

#### `.pose`

#### `.rssi`

#### `.battery_level`

#### `.emg`

## Enumerations

### `myo.Result`

### `myo.VibrationType`

### `myo.StreamEmg`

### `myo.Pose`

### `myo.EventType`

### `myo.HandlerResult`

### `myo.LockingPolicy`

### `myo.Arm`

### `myo.XDirection`

### `myo.UnlockType`

### `myo.UserActionType`

### `myo.WarmupState`

### `myo.WarmupResult`

## Exception

### `myo.Error`

### `myo.ResultError`

### `myo.InvalidOperation`

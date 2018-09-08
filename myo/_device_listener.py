# The MIT License (MIT)
#
# Copyright (c) 2015-2018 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import threading
import warnings
from ._ffi import EventType, Pose, VibrationType
from .utils import TimeoutManager
from .math import Vector, Quaternion


class DeviceListener(object):
  """
  Base class for device listeners -- objects that listen to Myo device events.
  """

  def on_event(self, event):
    if event.type.name:  # An event type that we know of.
      attr = 'on_' + event.type.name
      try:
        method = getattr(self, attr)
      except AttributeError:
        pass
      else:
        return method(event)

    warnings.warn('unhandled event: {}'.format(event))
    return True  # continue

  def on_paired(self, event): pass
  def on_unpaired(self, event): pass
  def on_connected(self, event): pass
  def on_disconnected(self, event): pass
  def on_arm_synced(self, event): pass
  def on_arm_unsynced(self, event): pass
  def on_unlocked(self, event): pass
  def on_locked(self, event): pass
  def on_pose(self, event): pass
  def on_orientation(self, event): pass
  def on_rssi(self, event): pass
  def on_battery_level(self, event): pass
  def on_emg(self, event): pass
  def on_warmup_completed(self, event): pass


class DeviceProxy(object):
  """
  Stateful container for Myo device data.
  """

  def __init__(self, device, timestamp, firmware_version, mac_address,
               condition_class=threading.Condition):
    self._device = device
    self._mac_address = mac_address
    self._cond = condition_class()
    self._pair_time = timestamp
    self._unpair_time = None
    self._connect_time = None
    self._disconnect_time = None
    self._emg = None
    self._orientation_update_index = 0
    self._orientation = Quaternion.identity()
    self._acceleration = Vector(0, 0, 0)
    self._gyroscope = Vector(0, 0, 0)
    self._pose = Pose.rest
    self._arm = None
    self._x_direction = None
    self._rssi = None
    self._battery_level = None
    self._firmware_version = firmware_version
    self._name = None

  def __repr__(self):
    with self._cond:
      con = 'connected' if self._connected else 'disconnected'
      return '<DeviceProxy ({}) name={!r}>'.format(con, self.name)

  @property
  def _connected(self):
    return self._connect_time is not None and self._disconnect_time is None

  @property
  def connected(self):
    with self._cond:
      return self._connected

  @property
  def paired(self):
    with self._cond:
      return self._unpair_time is not None

  @property
  def mac_address(self):
    return self._mac_address

  @property
  def pair_time(self):
    return self._pair_time

  @property
  def unpair_time(self):
    with self._cond:
      return self._unpair_time

  @property
  def connect_time(self):
    return self._connect_time

  @property
  def disconnect_time(self):
    with self._cond:
      return self._disconnect_time

  @property
  def firmware_version(self):
    return self._firmware_version

  @property
  def orientation_update_index(self):
    with self._cond:
      return self._orientation_update_index

  @property
  def orientation(self):
    with self._cond:
      return self._orientation.copy()

  @property
  def acceleration(self):
    with self._cond:
      return self._acceleration.copy()

  @property
  def gyroscope(self):
    with self._cond:
      return self._gyroscope.copy()

  @property
  def pose(self):
    with self._cond:
      return self._pose

  @property
  def arm(self):
    with self._cond:
      return self._arm

  @property
  def x_direction(self):
    with self._cond:
      return self._x_direction

  @property
  def rssi(self):
    with self._cond:
      return self._rssi

  @property
  def emg(self):
    with self._cond:
      return self._emg

  def set_locking_policy(self, policy):
    self._device.set_locking_policy(policy)

  def stream_emg(self, type):
    self._device.stream_emg(type)

  def vibrate(self, type=VibrationType.short):
    self._device.vibrate(type)

  def request_rssi(self):
    with self._cond:
      self._rssi = None
      self._device.request_rssi()

  def request_battery_level(self):
    with self._cond:
      self._battery_level = None
      self._device.request_battery_level()


class ApiDeviceListener(DeviceListener):

  def __init__(self, condition_class=threading.Condition):
    self._condition_class = condition_class
    self._cond = condition_class()
    self._devices = {}

  @property
  def devices(self):
    with self._cond:
      return list(self._devices.values())

  @property
  def connected_devices(self):
    with self._cond:
      return [x for x in self._devices.values() if x.connected]

  def wait_for_single_device(self, timeout=None, interval=0.5):
    """
    Waits until a Myo is was paired **and** connected with the Hub and returns
    it. If the *timeout* is exceeded, returns None. This function will not
    return a Myo that is only paired but not connected.

    # Parameters
    timeout: The maximum time to wait for a device.
    interval: The interval at which the function should exit sleeping. We can
      not sleep endlessly, otherwise the main thread can not be exit, eg.
      through a KeyboardInterrupt.
    """

    timer = TimeoutManager(timeout)
    with self._cond:
      # As long as there are no Myo's connected, wait until we
      # get notified about a change.
      while not timer.check():
        # Check if we found a Myo that is connected.
        for device in self._devices.values():
          if device.connected:
            return device
        self._cond.wait(timer.remainder(interval))

    return None

  def on_event(self, event):
    with self._cond:
      if event.type == EventType.paired:
        device = DeviceProxy(event.device, event.timestamp,
          event.firmware_version, self._condition_class)
        self._devices[device._device.handle] = device
        self._cond.notify_all()
        return
      else:
        try:
          if event.type == EventType.unpaired:
            device = self._devices.pop(event.device.handle)
          else:
            device = self._devices[event.device.handle]
        except KeyError:
          message = 'Myo device not in the device list ({})'
          warnings.warn(message.format(event), RuntimeWarning)
          return
      if event.type == EventType.unpaired:
        with device._cond:
          device._unpair_time = event.timestamp
        self._cond.notify_all()

    with device._cond:
      if event.type == EventType.connected:
        device._connect_time = event.timestamp
      elif event.type == EventType.disconnected:
        device._disconnect_time = event.timestamp
      elif event.type == EventType.emg:
        device._emg = event.emg
      elif event.type == EventType.arm_synced:
        device._arm = event.arm
        device._x_direction = event.x_direction
      elif event.type == EventType.rssi:
        device._rssi = event.rssi
      elif event.type == EventType.battery_level:
        device._battery_level = event.battery_level
      elif event.type == EventType.pose:
        device._pose = event.pose
      elif event.type == EventType.orientation:
        device._orientation_update_index += 1
        device._orientation = event.orientation
        device._gyroscope = event.gyroscope
        device._acceleration = event.acceleration

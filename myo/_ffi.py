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

import contextlib
import cffi
import os
import pkgutil
import re
import threading
import six
import sys

from .macaddr import MacAddress
from .math import Quaternion, Vector

try:
  from enum import IntEnum
except:
  from enum34 import IntEnum


##
# Exceptions
##

class Error(Exception):
  """
  Base class for errors and exceptions in the myo library.
  """


class ResultError(Error):
  """
  Raised if the result of an operation with the Myo library was anything
  but successful.
  """

  def __init__(self, kind, message):
    self.kind = kind
    self.message = message

  def __str__(self):
    return str((self.kind, self.message))


class InvalidOperation(Error):
  """
  Raised if an invalid operation is performed, for example if you attempt to
  read the firmware version in any event other than *paired* and *connect*.
  """


##
# Enumerations
##

class Result(IntEnum):
  __fallback__ = True
  success = 0
  error = 1
  error_invalid_argument = 2
  error_runtime = 3


class VibrationType(IntEnum):
  __fallback__ = True
  short = 0
  medium = 1
  long = 2


class StreamEmg(IntEnum):
  __fallback__ = True
  disabled = 0
  enabled = 1


class Pose(IntEnum):
  __fallback__ = True
  rest = 0
  fist = 1
  wave_in = 2
  wave_out = 3
  fingers_spread = 4
  double_tap = 5


Pose.num_poses = 6


class EventType(IntEnum):
  __fallback__ = True
  paired = 0
  unpaired = 1
  connected = 2
  disconnected = 3
  arm_synced = 4
  arm_unsynced = 5
  orientation = 6
  pose = 7
  rssi = 8
  unlocked = 9
  locked = 10
  emg = 11
  battery_level = 12
  warmup_completed = 13


class HandlerResult(IntEnum):
  __fallback__ = True
  continue_ = 0
  stop = 1


class LockingPolicy(IntEnum):
  __fallback__ = True
  none = 0      #: Pose events are always sent.
  standard = 1  #: (default) Pose events are not sent while a Myo is locked.


class Arm(IntEnum):
  __fallback__ = True
  right = 0
  left = 1
  unknown = 2


class XDirection(IntEnum):
  __fallback__ = True
  toward_wrist = 0
  toward_elbow = 1
  unknown = 2


class UnlockType(IntEnum):
  __fallback__ = True
  timed = 0
  hold = 1


class UserActionType(IntEnum):
  __fallback__ = True
  single = 0


class WarmupState(IntEnum):
  __fallback__ = True
  unknown = 0
  cold = 1
  warm = 2


class WarmupResult(IntEnum):
  __fallback__ = True
  unknown = 0
  success = 1
  failed_timeout = 2


##
# CFFI
##

def _getffi():
  string = pkgutil.get_data(__name__, 'libmyo.h').decode('utf8')
  string = string.replace('\r\n', '\n')
  # Remove stuff that cffi can not parse.
  string = re.sub('^\s*#.*$', '', string, flags=re.M)
  string = string.replace('LIBMYO_EXPORT', '')
  string = string.replace('extern "C" {', '')
  string = string.replace('} // extern "C"', '')

  ffi = cffi.FFI()
  ffi.cdef(string)
  return ffi


ffi = _getffi()
libmyo = None


def _getdlname():
  arch = 32 if sys.maxsize <= 2 ** 32 else 64
  if sys.platform.startswith('win32'):
    return 'myo{}.dll'.format(arch)
  elif sys.platform.startswith('darwin'):
    return 'myo'
  else:
    raise RuntimeError('unsupported platform: {!r}'.format(sys.platform))


def init(lib_name=None, bin_path=None, sdk_path=None):
  """
  Initialize the Myo SDK by loading the libmyo shared library. With no
  arguments, libmyo must be on your `PATH` or `LD_LIBRARY_PATH`.

  You can specify the exact path to libmyo with *lib_name*. Alternatively,
  you can specify the binaries directory that contains libmyo with *bin_path*.
  Finally, you can also pass the path to the Myo SDK root directory and it
  will figure out the path to libmyo by itself.
  """

  if sum(bool(x) for x in [lib_name, bin_path, sdk_path]) > 1:
    raise ValueError('expected zero or one argument(s)')

  if sdk_path:
    if sys.platform.startswith('win32'):
      bin_path = os.path.join(sdk_path, 'bin')
    elif sys.platform.startswith('darwin'):
      bin_path = os.path.join(sdk_path, 'myo.framework')
    else:
      raise RuntimeError('unsupported platform: {!r}'.format(sys.platform))
  if bin_path:
    lib_name = os.path.join(bin_path, _getdlname())
  if not lib_name:
    lib_name = _getdlname()

  global libmyo
  libmyo = ffi.dlopen(lib_name)


class _BaseWrapper(object):

  def __init__(self, handle):
    self._handle = handle

  @property
  def handle(self):
    return self._handle


class ErrorDetails(_BaseWrapper):
  """
  Wraps Myo error details information.
  """

  def __init__(self):
    super(ErrorDetails, self).__init__(ffi.new('libmyo_hub_t*'))

  def __del__(self):
    if self._handle[0]:
      libmyo.libmyo_free_error_details(self._handle[0])

  @property
  def kind(self):
    if self._handle[0]:
      result = Result(libmyo.libmyo_error_kind(self._handle[0]))
    else:
      result = Result.success
    return result

  @property
  def message(self):
    if self._handle[0]:
      return ffi.string(libmyo.libmyo_error_cstring(self._handle[0]))
    else:
      return ''

  @property
  def handle(self):
    return self._handle

  def raise_for_kind(self):
    kind = self.kind
    if kind != Result.success:
      raise ResultError(kind, self.message)


class Event(_BaseWrapper):

  def __init__(self, handle):
    super(Event, self).__init__(handle)
    self._type = EventType(libmyo.libmyo_event_get_type(self._handle))

  def __repr__(self):
    return 'Event(type={!r}, timestamp={!r}, mac_address={!r})'.format(
      self.type, self.timestamp, self.mac_address)

  @property
  def type(self):
    return self._type

  @property
  def timestamp(self):
    return libmyo.libmyo_event_get_timestamp(self._handle)

  @property
  def device(self):
    return Device(libmyo.libmyo_event_get_myo(self._handle))

  @property
  def device_name(self):
    return str(String(libmyo.libmyo_event_get_myo_name(self._handle)))

  @property
  def mac_address(self):
    if self.type == EventType.emg:
      return None
    return MacAddress(libmyo.libmyo_event_get_mac_address(self._handle))

  @property
  def firmware_version(self):
    return tuple(libmyo.libmyo_event_get_firmware_version(self._handle, x)
                 for x in [0, 1, 2, 3])

  @property
  def arm(self):
    if self.type != EventType.arm_synced:
      raise InvalidOperation()
    return Arm(libmyo.libmyo_event_get_arm(self._handle))

  @property
  def x_direction(self):
    if self.type != EventType.arm_synced:
      raise InvalidOperation()
    return XDirection(libmyo.libmyo_event_get_x_direction(self._handle))

  @property
  def warmup_state(self):
    if self.type != EventType.arm_synced:
      raise InvalidOperation()
    return WarmupState(libmyo.libmyo_event_get_warmup_state(self._handle))

  @property
  def warmup_result(self):
    if self.type != EventType.warmup_completed:
      raise InvalidOperation()
    return WarmupResult(libmyo.libmyo_event_get_warmup_result(self._handle))

  @property
  def rotation_on_arm(self):
    if self.type != EventType.arm_synced:
      raise InvalidOperation()
    return libmyo.libmyo_event_get_rotation_on_arm(self._handle)

  @property
  def orientation(self):
    if self.type != EventType.orientation:
      raise InvalidOperation()
    vals = (libmyo.libmyo_event_get_orientation(self._handle, i)
            for i in [0, 1, 2, 3])
    return Quaternion(*vals)

  @property
  def acceleration(self):
    if self.type != EventType.orientation:
      raise InvalidOperation()
    vals = (libmyo.libmyo_event_get_accelerometer(self._handle, i)
            for i in [0, 1, 2])
    return Vector(*vals)

  @property
  def gyroscope(self):
    if self.type != EventType.orientation:
      raise InvalidOperation()
    vals = (libmyo.libmyo_event_get_gyroscope(self._handle, i)
            for i in [0, 1, 2])
    return Vector(*vals)

  @property
  def pose(self):
    if self.type != EventType.pose:
      raise InvalidOperation()
    return Pose(libmyo.libmyo_event_get_pose(self._handle))

  @property
  def rssi(self):
    if self.type != EventType.rssi:
      raise InvalidOperation()
    return libmyo.libmyo_event_get_rssi(self._handle)

  @property
  def battery_level(self):
    if self.type != EventType.battery_level:
      raise InvalidOperation()
    return libmyo.libmyo_event_get_battery_level(self._handle)

  @property
  def emg(self):
    if self.type != EventType.emg:
      raise InvalidOperation()
    return [libmyo.libmyo_event_get_emg(self._handle, i) for i in range(8)]


class Device(_BaseWrapper):

  # libmyo_get_mac_address() is not in the Myo SDK 0.9.0 DLL.
  #@property
  #def mac_address(self):
  #  return MacAddress(libmyo.libmyo_get_mac_address(self._handle))

  def vibrate(self, type=VibrationType.medium):
    if not isinstance(type, VibrationType):
      raise TypeError('expected VibrationType')
    error = ErrorDetails()
    libmyo.libmyo_vibrate(self._handle, int(type), error.handle)
    return error.raise_for_kind()

  def stream_emg(self, type):
    if type is True: type = StreamEmg.enabled
    elif type is False: type = StreamEmg.disabled
    elif not isinstance(type, StreamEmg):
      raise TypeError('expected bool or StreamEmg')
    error = ErrorDetails()
    libmyo.libmyo_set_stream_emg(self._handle, int(type), error.handle)
    error.raise_for_kind()

  def request_rssi(self):
    error = ErrorDetails()
    libmyo.libmyo_request_rssi(self._handle, error.handle)
    error.raise_for_kind()

  def request_battery_level(self):
    error = ErrorDetails()
    libmyo.libmyo_request_battery_level(self._handle, error.handle)
    error.raise_for_kind()

  def unlock(self, type=UnlockType.hold):
    if not isinstance(type, UnlockType):
      raise TypeError('expected UnlockType')
    error = ErrorDetails()
    libmyo.libmyo_myo_unlock(self._handle, int(type), error.handle)
    error.raise_for_kind()

  def lock(self):
    error = ErrorDetails()
    libmyo.libmyo_myo_lock(self._handle, error.handle)
    error.raise_for_kind()

  def notify_user_action(self, type=UserActionType.single):
    if not isinstance(type, UserActionType):
      raise TypeError('expected UserActionType')
    error = ErrorDetails()
    libmyo.libmyo_myo_notify_user_action(self._handle, int(type), error.handle)
    error.raise_for_kind()


class String(_BaseWrapper):

  def __str__(self):
    return ffi.string(libmyo.libmyo_string_c_str(self._handle)).decode('utf8')

  def __del__(self):
    libmyo.libmyo_string_free(self._handle)


class Hub(_BaseWrapper):
  """
  Low-level wrapper for a Myo Hub object.
  """

  def __init__(self, application_identifier='com.niklasrosenstein.myo-python'):
    super(Hub, self).__init__(ffi.new('libmyo_hub_t*'))
    error = ErrorDetails()
    libmyo.libmyo_init_hub(self._handle, application_identifier.encode('ascii'), error.handle)
    error.raise_for_kind()
    self.locking_policy = LockingPolicy.none
    self._lock = threading.Lock()
    self._running = False
    self._stop_requested = False
    self._stopped = False

  def __del__(self):
    if self._handle[0]:
      error = ErrorDetails()
      libmyo.libmyo_shutdown_hub(self._handle[0], error.handle)
      error.raise_for_kind()

  @property
  def handle(self):
    return self._handle

  @property
  def locking_policy(self):
    return self._locking_policy

  @locking_policy.setter
  def locking_policy(self, policy):
    if not isinstance(policy, LockingPolicy):
      raise TypeError('expected LockingPolicy')
    error = ErrorDetails()
    libmyo.libmyo_set_locking_policy(self._handle[0], int(policy), error.handle)
    error.raise_for_kind()

  @property
  def running(self):
    with self._lock:
      return self._running

  def run(self, handler, duration_ms):
    """
    Runs the *handler* function for *duration_ms* milliseconds. The function
    must accept exactly one argument which is an #Event object. The handler
    must return either a #HandlerResult value, #False, #True or #None, whereas
    #False represents #HandlerResult.stop and #True and #None represent
    #HandlerResult.continue_.

    If the run did not complete due to the handler returning #HandlerResult.stop
    or #False or the procedure was cancelled via #Hub.stop(), this function
    returns #False. If the full *duration_ms* completed, #True is returned.

    This function blocks the caller until either *duration_ms* passed, the
    handler returned #HandlerResult.stop or #False or #Hub.stop() was called.
    """

    if not callable(handler):
      if hasattr(handler, 'on_event'):
        handler = handler.on_event
      else:
        raise TypeError('expected callable or DeviceListener')

    with self._lock:
      if self._running:
        raise RuntimeError('a handler is already running in the Hub')
      self._running = True
      self._stop_requested = False
      self._stopped = False

    exc_box = []

    def callback_on_error(*exc_info):
      exc_box.append(exc_info)
      with self._lock:
        self._stopped = True
      return HandlerResult.stop

    def callback(_, event):
      with self._lock:
        if self._stop_requested:
          self._stopped = True
          return HandlerResult.stop

      result = handler(Event(event))
      if result is None or result is True:
        result = HandlerResult.continue_
      elif result is False:
        result = HandlerResult.stop
      else:
        result = HandlerResult(result)
      if result == HandlerResult.stop:
        with self._lock:
          self._stopped = True

      return result

    cdecl = 'libmyo_handler_result_t(void*, libmyo_event_t)'
    callback = ffi.callback(cdecl, callback, onerror=callback_on_error)

    try:
      error = ErrorDetails()
      libmyo.libmyo_run(self._handle[0], duration_ms, callback, ffi.NULL, error.handle)
      error.raise_for_kind()
      if exc_box:
        six.reraise(*exc_box[0])
    finally:
      with self._lock:
        self._running = False
        result = not self._stopped

    return result

  def run_forever(self, handler, duration_ms=500):
    while self.run(handler, duration_ms):
      if self._stop_requested:
        break

  @contextlib.contextmanager
  def run_in_background(self, handler, duration_ms=500):
    thread = threading.Thread(target=lambda: self.run_forever(handler, duration_ms))
    thread.start()
    try:
      yield thread
    finally:
      self.stop()

  def stop(self):
    with self._lock:
      self._stop_requested = True


__all__ = [
  'Error', 'ResultError', 'InvalidOperation',

  'Result', 'VibrationType', 'StreamEmg', 'Pose', 'EventType', 'LockingPolicy',
  'Arm', 'XDirection', 'UnlockType', 'UserActionType', 'WarmupState',
  'WarmupResult',

  'Event', 'Device', 'Hub', 'init'
]

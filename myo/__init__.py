# Copyright (c) 2015  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
:mod:`myo` - Python bindings for the Myo SDK
============================================
"""

__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '0.2.2'
__license__ = 'MIT'

from .lowlevel import enums
from .lowlevel.enums import *

__all__ = [
    'Hub', 'DeviceListener', 'Event', 'myo_init', 'myo_initialized',
    # Backwards compatibility
    'init_myo', 'event_type', 'pose', 'locking_policy'] + enums.__all__

# The version of the Myo SDK that the library was recently
# updated for.
myo_sdk_version = '0.9.0'

from . import lowlevel as _myo
from .lowlevel import error, ResultError, InvalidOperation
from .vector import Vector
from .quaternion import Quaternion
from .device_listener import DeviceListener, Feed

import time
import threading
import traceback
import sys
import warnings

init = myo_init = _myo.lib.init
myo_initialized = _myo.lib.initialized


class Hub(object):
    """
    High-level interface for the Myo Hub which manages data processing
    and event triggering for a Myo device.

    .. note::

        There can only be one Hub instance. The constructor of the
        :class:`Hub` class will return the existing instance if
        it has not been shut down since then.
    """

    def __init__(self):
        super(Hub, self).__init__()
        self._lock = threading.RLock()
        self._running = False
        self._stopped = False
        self._exception = None
        self._thread = None
        self._hub = None
        self._locking_policy = LockingPolicy.none
        self._new()

    def __str__(self):
        parts = ['<Hub ']
        with self._lock:
            if self._running:
                if self._stopped:
                    parts.append('stop requested')
                else:
                    parts.append('running')
            else:
                parts.append('stopped')
        return ' '.join(parts) + '>'

    def __nonzero__(self):
        return bool(self._hub)

    __bool__ = __nonzero__  # Python 3

    def _new(self):
        assert not self._hub
        self._hub = _myo.Hub()
        self._hub.set_locking_policy(self._locking_policy)

    def _assert_running(self):
        with self._lock:
            if not self._running:
                raise RuntimeError('Hub is not running')

    @property
    def running(self):
        """
        :return: True if the Hub is running, False if not.
        """

        with self._lock:
            return self._running

    @property
    def stop_requested(self):
        """
        :return: True if the Hub has been stopped with a call to
            :meth:`stop`, False if not. The Hub could still be
            running though.
        """

        with self._lock:
            return self._stopped

    stopped = stop_requested  # Backwards compatibility

    @property
    def exception(self):
        """
        Set when an exception occured within the listener. The
        Hub can not be re-run if this is set. Use
        :meth:`clear_exception` to remove the exception from the Hub.
        """

        with self._lock:
            return self._exception

    def clear_exception(self):
        """
        If an exception is set, the Hub can not be re-run. This
        method will clear the stored exception if there is any.
        """

        with self._lock:
            self._exception = None

    def set_locking_policy(self, locking_policy):
        """
        Sets the locking policy.
        """

        with self._lock:
            if self._hub:
                self._hub.set_locking_policy(locking_policy)
            self._locking_policy = locking_policy

    def run_once(self, duration_ms, listener):
        """
        Run *listener* for *duration_ms* seconds.
        """

        if not isinstance(listener, DeviceListener):
            raise TypeError('listener must be DeviceListener instance')

        # If there is an exception set, an exception occured
        # in the listener and we will not do anything further!
        with self._lock:
            if self._exception:
                message = 'exception occured in listener, can not rerun'
                raise RuntimeError(message, self._exception)

        def callback(listener, event):
            try:
                with self._lock:
                    if self._stopped:
                        return False
                    return _invoke_listener(listener, event)
            except BaseException:
                with self._lock:
                    self._exception = sys.exc_info()
                raise

        return self._hub.run(duration_ms, callback, listener)

    def run(self, interval_ms, listener, lil_sleep=0.01):
        """
        Run the Hub with an execution interval of *interval_ms*
        and the specified *listener* until the Hub was stopped. This
        method does not block the main thread. Returns the thread
        object that was created.

        The Hub and its thread will stop as soon as :meth:`stop`
        was called or the :class:`DeviceListener` returns False
        from one of its callback methods.

        *lil_sleep* specifies a number of seconds to sleep after
        the Hub has been started. This will allow the Hub thread
        to start before anything else is called.
        """

        if not isinstance(listener, DeviceListener):
            raise TypeError('listener must be DeviceListener instance')

        # Make sure the Hub doesn't run already and set
        # the running flag to True.
        with self._lock:
            if self._running:
                raise RuntimeError('Hub is already running')
            self._running = True
            if not self._hub:
                self._new()

        # This is the worker function that is running in
        # a new thread.
        def worker():
            try:
                while not self.stop_requested:
                    if not self.run_once(interval_ms, listener):
                        self.stop()
            finally:
                with self._lock:
                    self._running = False
                    self._stopped = False

        with self._lock:
            self._thread = threading.Thread(target=worker)
            self._thread.start()

        # Little sleeping so we can immediately call pair_any()
        # or variants.
        if lil_sleep:
            time.sleep(lil_sleep)

    def stop(self, join=False):
        """
        Request the Stop of the Hub when it is running. When
        *join* is True, this function will block the current thread
        until the Hub is not :attr:`running` anymore.
        """

        with self._lock:
            self._stopped = True
        if join: self.join()

    def join(self, timeout=None):
        """
        If the Hub was run with a thread, it can be joined (waiting
        blocked) with this method. If the Hub was not started within a
        thread, this method will do nothing.
        """

        with self._lock:
            if not self._thread:
                return
            if not self._thread.is_alive():
                self._thread = None
                return
            thread = self._thread

        thread.join(timeout)
        with self._lock:
            if not thread.is_alive():
                self._thread = None

    def shutdown(self):
        """
        Shut the hub down. If the hub is still running, it will be
        stopped right where it is. Call it before the hub is being
        garbage collected, or a warning will be printed that it has not
        been called.

        Do not call this method from a DeviceListener as it would
        cause the current thread to be joined which is not possible.
        Use :meth:`stop` to request a stop.
        """

        self.stop()
        try:
            self.join()
        except RuntimeError:
            message = 'Hub.shutdown() must not be called from DeviceListener'
            raise RuntimeError(message)

        with self._lock:
            if self._hub:
                self._hub.shutdown()


def _invoke_listener(listener, event):
    """
    Invokes the :class:`DeviceListener` callback methods for
    the specified :class:`event<myo.lowlevel.event_t>`. If any
    of the callbacks return False, this function will return False
    as well. It also issues a warning when a DeviceListener method
    did not return None or a boolean value.

    :meth:`DeviceListener.on_event_finished` is always called,
    event when any of the calls in between returned False already.
    """

    myo = event.myo
    timestamp = event.timestamp

    # Invokes a method on the listener. If defaults=True, will prepend
    # the myo and timestamp argument to *args.
    def _(name, *args, **kwargs):
        defaults = kwargs.pop('defaults', True)
        if kwargs:
            raise TypeError('unexpected arguments')

        if defaults:
            args = (myo, timestamp) + tuple(args)
        method = getattr(listener, name)
        result = method(*args)

        if result is None:
            return True
        elif not isinstance(result, bool):
            sys.stderr.write('DeviceListener.%s() must return None or bool\n' % name)
            result = False

        return result

    kind = event.type
    result = _('on_event', kind, event, defaults=False)

    if kind == EventType.paired:
        result = result and _('on_pair', event.firmware_version)
    elif kind == EventType.unpaired:
        result = result and _('on_unpair')
    elif kind == EventType.connected:
        result = result and _('on_connect', event.firmware_version)
    elif kind == EventType.disconnected:
        result = result and _('on_disconnect')
    elif kind == EventType.arm_synced:
        result = result and _('on_arm_sync', event.arm, event.x_direction,
                              event.rotation, event.warmup_state)
    elif kind == EventType.arm_unsynced:
        result = result and _('on_arm_unsync')
    elif kind == EventType.unlocked:
        result = result and _('on_unlock')
    elif kind == EventType.locked:
        result = result and _('on_lock')
    elif kind == EventType.pose:
        result = result and _('on_pose', event.pose)
    elif kind == EventType.orientation:
        result = result and _('on_orientation_data', event.orientation)
        result = result and _('on_accelerometor_data', event.acceleration)
        result = result and _('on_gyroscope_data', event.gyroscope)
    elif kind == EventType.rssi:
        result = result and _('on_rssi', event.rssi)
    elif kind == EventType.bettery_level:
        result = result and _('on_battery_level_received', event.level)
    elif kind == EventType.emg:
        result = result and _('on_emg_data', event.emg)
    elif kind == EventType.warmup_completed:
        result = result and _('on_warmup_completed', event.warmup_result)
    elif kind.name:
        warnings.warn('unhandled myo.EventType: {0}'.format(kind.name), RuntimeWarning)
    else:
        warnings.warn('unknown myo.EventType: {0}'.format(kind.value), RuntimeWarning)

    if not _('on_event_finished', kind, event, defaults=False):
        result = False
    return result

# Backwards compatibility
event_type = EventType
pose = Pose
locking_policy = LockingPolicy
init_myo = myo_init

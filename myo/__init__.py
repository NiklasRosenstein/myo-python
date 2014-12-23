# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.
r"""
myo - Highlevel Myo SDK Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a Hub, a DeviceListener and get started!

---------------------------------

__Copyright (C) 2014  Niklas Rosenstein__,
All rights reserved.
"""

__author__ = ('Niklas Rosenstein', 'rosensteinniklas@gmail.com')
__version__ = (0, 1, 0)

# The latest version number of the Myo SDK that this library
# is compatible with.
sdk_version = 5

__all__ = (
    # High level classes
    'Hub', 'DeviceListener', 'Event',

    # Initializers and global functions.
    'init_myo', 'myo_initialized', 'now',

    # Enumerations
    'event_type', 'pose', 'locking_policy'
)

from myo import lowlevel as _myo
from myo.lowlevel import init, initialized, now
from myo.lowlevel import MyoError, ResultError, InvalidOperation
from myo.lowlevel import event_type_t as event_type, pose_t as pose
from myo.lowlevel import locking_policy_t as locking_policy
import time
import threading
import traceback
import sys

init_myo = init
myo_initialized = initialized

class Hub(object):
    r""" Wrapper for a Myo Hub which manages the data processing
    and event triggering for a Myo device.

    .. note:: There can only be one Hub instance. The constructor
    of the :class:`Hub` class will return the existing instance if
    it has not been shut down since then. """

    def __init__(self):
        super(Hub, self).__init__()

        self._lock = threading.RLock()
        self._hub = _myo.hub_t.init_hub()
        self._running = False
        self._stopped = False
        self._exception = None
        self._thread = None

    def __str__(self):
        parts = ['<Hub ']
        if not self._hub:
            parts.append('shut down')
        else:
            with self._lock:
                if self._running:
                    parts.append('running')
                if self._stopped:
                    parts.append('stop-requested')

        return ' ,'.join(parts) + '>'

    def __nonzero__(self):
        return bool(self._hub)
    __bool__ = __nonzero__

    def _assert_running(self):
        with self._lock:
            if not self._running:
                raise RuntimeError('Hub is not running')

    @property
    def running(self):
        r""" True when the Hub is still running (ie. processing data
        from Myo(s) in another thread). """

        with self._lock:
            return self._running

    @property
    def stopped(self):
        r""" True if the Hub has been stopped with a call to
        :meth:`stop`, False if not. When this is True, the Hub
        could still be :attr:`running`. """

        with self._lock:
            return self._stopped

    @property
    def exception(self):
        r""" Set when an exception occured within the listener. The
        Hub can not be re-run if this is set. Use :meth:`clear_exception`
        to remove the exception from the Hub. """

        with self._lock:
            return self._exception

    def clear_exception(self):
        r""" If an exception is set, the Hub can not be re-run. This
        method will clear the stored exception if there is any. """

        with self._lock:
            self._exception = None

    def pair_any(self, n=1):
        with self._lock:
            self._assert_running()
            self._hub.pair_any(n)

    def pair_by_mac_address(self, mac_address):
        with self._lock:
            self._assert_running()
            self._hub.pair_by_mac_address(mac_address)

    def pair_adjacent(self, n=1):
        with self._lock:
            self._assert_running()
            self._hub.pair_adjacent(n)

    def set_locking_policy(self, locking_policy):
        with self._lock:
            self._hub.set_locking_policy(locking_policy)

    def _run(self, duration_ms, listener):
        r""" Private version of the :meth:`run` method. Does not
        re-set the :attr:`running` attribute. Used by :meth:`run`.
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
            # Stop immediately if the Hub was stopped via the
            # stop() method.
            with self._lock:
                if self._stopped:
                    return False

            # Invoke the listener but catch the event.
            try:
                return _invoke_listener(listener, event)
            except Exception as exc:
                traceback.print_exc()
                with self._lock:
                    self._exception = exc

            return False

        return self._hub.run(duration_ms, callback, listener)

    def run(self, interval_ms, listener, lil_sleep=0.01):
        r""" Run the Hub with an execution interval of *interval_ms*
        and the specified *listener* until the Hub was stopped. This
        method does not block the main thread. Returns the thread
        object that was created.

        The Hub and its thread will stop as soon as :meth:`stop`
        was called or the :class:`DeviceListener` returns False
        from one of its callback methods.

        *lil_sleep* specifies a number of seconds to sleep after
        the Hub has been started. This will allow the Hub thread
        to start before anything else is called."""

        if not isinstance(listener, DeviceListener):
            raise TypeError('listener must be DeviceListener instance')

        # Make sure the Hub doesn't run already and set
        # the running flag to True.
        with self._lock:
            if self._running:
                raise RuntimeError('Hub is already running')
            self._running = True

        # This is the worker function that is running in
        # a new thread.
        def worker():
            while not self.stopped:
                if not self._run(interval_ms, listener):
                    self.stop()

            with self._lock:
                self._running = False

        with self._lock:
            self._thread = threading.Thread(target=worker)
            self._thread.start()

        # Little sleeping so we can immediately call pair_any()
        # or variants.
        if lil_sleep:
            time.sleep(lil_sleep)

    def stop(self, join=False):
        r""" Request the Stop of the Hub when it is running. When
        *join* is True, this function will block the current thread
        until the Hub is not :attr:`running` anymore. """

        with self._lock:
            self._stopped = True
        if join: self.join()

    def join(self, timeout=None):
        r""" If the Hub was run with a thread, it can be joined (waiting
        blocked) with this method. If the Hub was not started within a
        thread, this method will do nothing. """

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
        r""" Shut the hub down. Will happen automatically when
        the Hub is being deleted. This method will cause the Hub
        to stop if it was still running. """

        self.stop()
        try:
            self.join()
        except RuntimeError:
            message = 'Hub.shutdown() must not be called from DeviceListener'
            raise RuntimeError(message)

        self._hub.shutdown()

class DeviceListener(object):
    r""" Interface for listening to data sent from a Myo device.
    Return False from one of its callback methods to instruct
    the Hub to stop processing. """

    def on_event(self, event):
        r""" Called before any of the event callbacks. """

    def on_event_finished(self, event):
        r""" Called after the respective event callbacks have been
        invoked. This method is *always* triggered, even if one of
        the callbacks requested the stop of the Hub. """

    def on_pair(self, myo, timestamp):
        pass

    def on_connect(self, myo, timestamp):
        pass

    def on_disconnect(self, myo, timestamp):
        pass

    def on_pose(self, myo, timestamp, pose):
        pass

    def on_orientation_data(self, myo, timestamp, orientation):
        pass

    def on_accelerometor_data(self, myo, timestamp, acceleration):
        pass

    def on_gyroscope_data(self, myo, timestamp, gyroscope):
        pass

    def on_rssi(self, myo, timestamp, rssi):
        pass

    def on_emg(self, myo, timestamp, emg):
        pass

class Event(object):
    r""" Copy of a Myo SDK event object that can be accessed even
    after the event has been destroyed. Must be constructed with
    a :class:`myo.lowlevel.event_t` object.

    This type of object is passed to :meth:`DeviceListener.on_event`. """

    def __init__(self, low_event):
        if not isinstance(low_event, _myo.event_t):
            raise TypeError('expected event_t object')
        super(Event, self).__init__()
        self.type = low_event.type
        self.myo = low_event.myo
        self.timestamp = low_event.timestamp

        if self.type in [event_type.paired, event_type.connected]:
            self.firmware_version = low_event.firmware_version
        elif self.type == event_type.orientation:
            self.orientation = low_event.orientation
            self.acceleration = low_event.acceleration
            self.gyroscope = low_event.gyroscope
        elif self.type == event_type.pose:
            self.pose = low_event.pose
        elif self.type == event_type.rssi:
            self.rssi = low_event.rssi
        elif self.type == event_type.emg:
            self.emg = low_event.emg

    def __str__(self):
        return '<Event %s>' % self.type

def _invoke_listener(listener, event):
    r""" Invokes the :class:`DeviceListener` callback methods for
    the specified :class:`event<myo.lowlevel.event_t>`. If any
    of the callbacks return False, this function will return False
    as well. It also issues a warning when a DeviceListener method
    did not return None or a boolean value.

    :meth:`DeviceListener.on_event_finished` is always called,
    event when any of the calls in between returned False already. """

    event = Event(event)
    myo = event.myo
    timestamp = event.timestamp
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
    result = _('on_event', event, defaults=False)

    if kind == _myo.event_type_t.paired:
        result = result and _('on_pair')

    elif kind == _myo.event_type_t.connected:
        result = result and _('on_connect')

    elif kind == _myo.event_type_t.disconnected:
        result = result and _('on_disconnect')

    elif kind == _myo.event_type_t.pose:
        result = result and _('on_pose', event.pose)

    elif kind == _myo.event_type_t.orientation:
        result = result and _('on_orientation_data', event.orientation)
        result = result and _('on_accelerometor_data', event.acceleration)
        result = result and _('on_gyroscope_data', event.gyroscope)

    elif kind == _myo.event_type_t.rssi:
        result = result and _('on_rssi', event.rssi)

    elif kind == _myo.event_type_t.emg:
        result = result and _('on_emg', event.emg)

    elif kind == _myo.event_type_t.arm_unsynced:
        result = result and _('on_unsync')
    elif kind == _myo.event_type_t.arm_synced:
        result = result and _('on_sync')

    elif kind == _myo.event_type_t.unlocked:
        result = result and _('on_unlock')

    elif kind == _myo.event_type_t.locked:
        result = result and _('on_lock')

    else:
        print('invalid event type: %s' % kind)

    if not _('on_event_finished', event, defaults=False):
        result = False
    return result


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
    'init_myo', 'myo_is_initialized', 'now', 'Hub', 'DeviceListener',
)

from myo import lowlevel as _myo
from myo.lowlevel import MyoError, ResultError, InvalidOperation

import time
import threading
import traceback

init = init_myo = _myo.init
is_initialized = myo_is_initialized = _myo.is_initialized
now = _myo.now

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

    def _assert_running(self):
        with self._lock:
            if not self._running:
                raise RuntimeError('Hub is not running')

    @property
    def running(self):
        with self._lock:
            return self._running

    @property
    def exception(self):
        r""" Set when an exception occured within the listener. The
        Hub can not be re-run if this is set. Use :meth:`clear_exception`
        to remove the exception from the Hub. """

        with self._lock:
            return self._exception

    def stop(self):
        r""" Stop the Hub if it is running. Raise a RuntimeError if
        the Hub is not running. """

        with self._lock:
            if not self._running:
                raise RuntimeError('Hub is not running')
            self._stopped = True

    @property
    def stopped(self):
        r""" Returns True if the Hub has been instructed to stop,
        False if not. """

        with self._lock:
            return self._stopped

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

    def _run(self, duration_ms, listener):
        r""" Private version of the :meth:`run` method. Does not
        re-set the :attr:`running` attribute. Used by :meth:`run`
        and :meth:`async_until_stopped`. """

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

    def run(self, duration_ms, listener):
        r""" Run the Hub for *duration_ms* milliseconds. Raises
        a RuntimeError when an exception occured in the listener the
        last time the Hub was run. :prop:`stopped` will return False
        after this method was successfully started.

        This is a blocking method. It returns True when the run
        was complete, but False when the :class:`DeviceListener`
        caused the Hub to stop handling the Myo(s) by returning
        False from one of its callbacks. """

        # Make sure that the hub is not already running. We
        # can't run it twice.
        with self._lock:
            if self._running:
                raise RuntimeError('Hub is already running')
            self._running = True

        # Invoke the run process, this will block the current thread-
        result = self._run(duration_ms, listener)

        with self._lock:
            self._running = False
        return result

    def async_until_stopped(self, interval_ms, listener, lil_sleep=0.01):
        r""" Runs the Hub with an execution interval of *interval_ms*
        and the specified *listener* until the Hub was stopped. This
        method does not block the main thread. Returns the thread
        object that was created.

        The Hub and its thread will stop as soon as :meth:`stop`
        was called or the :class:`DeviceListener` returned False
        from one of its callback methods. """

        if not isinstance(listener, DeviceListener):
            raise TypeError('listener must be DeviceListener instance')

        # Make sure the Hub doesn't run already and set
        # the running flag to True.
        with self._lock:
            if self._running:
                raise RuntimeError('Hub is already running')
            self._running = True

        # Just for safety reasons, if the worker thread is
        # still running be the hub is officially not, we did
        # something wrong.
        if self._thread and self._thread.is_alive():
            message = 'Thread is still alive, yet the Hub is not ' \
                      'running. This is a strange error that should ' \
                      'not actually occur ;-)'
            raise RuntimeError(message)

        # Threaded worker function.
        def worker():
            while not self.stopped:
                if not self._run(interval_ms, listener):
                    self.stop()

        self._thread = threading.Thread(target=worker)
        self._thread.start()

        # Little sleeping so we can immediately call pair_any()
        # or variants.
        if lil_sleep:
            time.sleep(lil_sleep)

    def join(self, timeout=None):
        r""" If the Hub was run with a thread, it can be joined (waiting
        blocked) with this method. Can not be called twice without
        re-starting the Hub. """

        if not self._thread:
            raise RuntimeError('Hub is not attached to a thread')
        self._thread.join(timeout)
        self._thread = None

    def shutdown(self):
        r""" Shut the hub down. Not a required call. A new instance
        of the :class:`Hub` constructor will then return a new
        instance of the class. """

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

def _invoke_listener(listener, event):
    r""" Invokes the :class:`DeviceListener` callback methods for
    the specified :class:`event<myo.lowlevel.event_t>`. If any
    of the callbacks return False, this function will return False
    as well. It also issues a warning when a DeviceListener method
    did not return None or a boolean value.

    :meth:`DeviceListener.on_event_finished` is always called,
    event when any of the calls in between returned False already. """

    myo = event.myo
    timestamp = event.timestamp
    def _(name, *args, **kwargs):
        defaults = kwargs.pop('defaults', True)

        if defaults:
            args = (myo, timestamp) + tuple(args)
        method = getattr(listener, name)
        result = method(*args)

        if result is None:
            return True
        elif not isinstance(result, bool):
            message = 'DeviceListener.%s() must return None or bool'
            warnings.warn(message % name)
            result = False

        return result

    kind = event.type
    result = _('on_event', event, default=False)

    if type_ == _myo.event_type_t.paired:
        result = result and _('on_pair')

    elif type_ == _myo.event_type_t.connected:
        result = result and _('on_connect')

    elif type_ == _myo.event_type_t.disconnected:
        result = result and _('on_disconnect')

    elif type_ == _myo.event_type_t.pose:
        result = result and _('on_pose', event.pose)

    elif type_ == _myo.event_type_t.orientation:
        result = result and _('on_orientation_data', event.orientation)
        result = result and _('on_accelerometor_data', event.acceleration)
        result = result and _('on_gyroscope_data', event.gyroscope)

    elif type_ == _myo.event_type_t.rssi:
        result = result and _('on_rssi', event.rssi)

    else:
        raise RuntimeError('invalid event type', type_)

    if not _('on_event_finished', event, default=False):
        result = False
    return result


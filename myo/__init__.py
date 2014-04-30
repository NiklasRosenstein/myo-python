# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.

__author__ = ('Niklas Rosenstein', 'rosensteinniklas@gmail.com')
__version__ = (0, 1, 0)

# The latest version number of the Myo SDK that this library
# is compatible with.
sdk_version = 5

from myo import lowlevel as _myo
init = _myo.init

import time
import threading

class Hub(object):
    r""" Wrapper for a Myo Hub which manages the data processing
    and event triggering for a Myo device. """

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

    def run(self, duration_ms, listener):
        r""" Run the Hub for *duration_ms* milliseconds. Raises
        a RuntimeError when an exception occured in the listener the
        last time the Hub was run. :prop:`stopped` will return False
        after this method was successfully started.

        This is a blocking method. """

        if not isinstance(listener, DeviceListener):
            raise TypeError('listener must be DeviceListener instance')

        # If there is an exception set, an exception occured
        # in the listener and we will not do anything further!
        with self._lock:
            if self._exception:
                message = 'exception occured in listener, can not rerun'
                raise RuntimeError(message, self._exception)
            if self._running:
                raise RuntimeError('Hub is already running')
            self._running = True

        def callback(listener, event):
            # Stop immediately if the Hub was stopped via the
            # stop() method.
            with self._lock:
                if self._stopped:
                    return False

            # Invoke the listener but catch the event.
            try:
                return invoke_listener(listener, event)
            except Exception as exc:
                traceback.print_exc()
                with self._lock:
                    self._exception = exc

            return False

        # Run the hub.
        self._hub.run(duration_ms, callback, listener)
        with self._lock:
            self._running = False

    def asnyc_till_stopped(self, interval_ms, listener, lil_sleep=0.01):
        r""" Runs the Hub with an execution interval of *interval_ms*
        and the specified *listener* until the Hub was stopped. This
        method does not block the main thread. Returns the thread
        object that was created. """

        if not isinstance(listener, DeviceListener):
            raise TypeError('listener must be DeviceListener instance')
        if self.running:
            raise RuntimeError('Hub is already running')
        if self._thread and self._thread.is_alive():
            raise RuntimeError('Thread is still alive, yet the Hub is not '
                    'running. This is a strange error that should not '
                    'actually occur ;-)')

        def worker():
            while not self.stopped:
                self.run(interval_ms, listener)

        self._thread = threading.Thread(target=worker)
        self._thread.start()

        # Little sleeping so we can immediately call pair_any()
        # or variants.
        if lil_sleep:
            time.sleep(lil_sleep)

    def join(self, timeout=None):
        r""" If the Hub was run with a thread, it can be joined (waiting
        blocked) with this method. """

        if not self._thread:
            raise RuntimeError('Hub is not attached to a thread')
        self._thread.join(timeout)

class DeviceListener(object):
    r""" Interface for listening to data sent from a Myo device. """

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

def invoke_listener(listener, event):

    myo = event.myo
    timestamp = event.timestamp
    type_ = event.type

    if type_ == _myo.event_type_t.paired:
        result = listener.on_pair(myo, timestamp)

    elif type_ == _myo.event_type_t.connected:
        result = listener.on_connect(myo, timestamp)

    elif type_ == _myo.event_type_t.disconnected:
        result = listener.on_disconnect(myo, timestamp)

    elif type_ == _myo.event_type_t.pose:
        result = listener.on_pose(myo, timestamp, event.pose)

    elif type_ == _myo.event_type_t.orientation:
        result = listener.on_orientation_data(myo, timestamp, event.orientation)
        result = result and listener.on_accelerometor_data(myo, timestamp, event.acceleration)
        result = result and listener.on_gyroscope_data(myo, timestamp, event.gyroscope)

    elif type_ == _myo.event_type_t.rssi:
        result = listener.on_rssi(myo, timestamp, event.rssi)
    else:
        raise RuntimeError('invalid event type', type_)

    if result is None:
        return True
    return result


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

import abc
import six
import time
import threading
import warnings

from .lowlevel.enums import EventType, Pose, Arm, XDirection
from .utils.threading import TimeoutClock
from .vector import Vector
from .quaternion import Quaternion


class DeviceListener(object):
    """
    Interface for listening to data sent from a Myo device.
    Return False from one of its callback methods to instruct
    the Hub to stop processing.

    The *DeviceListener* operates between the high and low level
    of the myo Python bindings. The ``myo`` object that is passed
    to callback methods is a :class:`myo.lowlevel.ctyping.Myo`
    object.
    """

    def on_event(self, kind, event):
        """
        Called before any of the event callbacks.
        """

    def on_event_finished(self, kind, event):
        """
        Called after the respective event callbacks have been
        invoked. This method is *always* triggered, even if one of
        the callbacks requested the stop of the Hub.
        """

    def on_pair(self, myo, timestamp, firmware_version):
        pass

    def on_unpair(self, myo, timestamp):
        pass

    def on_connect(self, myo, timestamp, firmware_version):
        pass

    def on_disconnect(self, myo, timestamp):
        pass

    def on_arm_sync(self, myo, timestamp, arm, x_direction, rotation,
                    warmup_state):
        pass

    def on_arm_unsync(self, myo, timestamp):
        pass

    def on_unlock(self, myo, timestamp):
        pass

    def on_lock(self, myo, timestamp):
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

    def on_battery_level_received(self, myo, timestamp, level):
        pass

    def on_emg_data(self, myo, timestamp, emg):
        pass

    def on_warmup_completed(self, myo, timestamp, warmup_result):
        pass


class Feed(DeviceListener):
    """
    This class implements the :class:`DeviceListener` interface
    to collect all data and make it available to another thread
    on-demand.

    .. code-block:: python

        import myo as libmyo
        feed = libmyo.device_listener.Feed()
        hub = libmyo.Hub()
        hub.run(1000, feed)

        try:
            while True:
                myos = feed.get_connected_devices()
                if myos:
                    print myos[0], myos[0].orientation
                time.sleep(0.5)
        finally:
            hub.stop(True)
            hub.shutdown()
    """

    class MyoProxy(object):

        __slots__ = (
            'synchronized,_pair_time,_unpair_time,_connect_time,'
            '_disconnect_time,_myo,_emg,_orientation,_acceleration,'
            '_gyroscope,_pose,_arm,_xdir,_rssi,_firmware_version').split(',')

        def __init__(self, low_myo, timestamp, firmware_version):
            super(Feed.MyoProxy, self).__init__()
            self.synchronized = threading.Condition()
            self._pair_time = timestamp
            self._unpair_time = None
            self._connect_time = None
            self._disconnect_time = None
            self._myo = low_myo
            self._emg = None
            self._orientation = Quaternion.identity()
            self._acceleration = Vector(0, 0, 0)
            self._gyroscope = Vector(0, 0, 0)
            self._pose = Pose.rest
            self._arm = None
            self._xdir = None
            self._rssi = None
            self._firmware_version = firmware_version

        def __repr__(self):
            result = '<MyoProxy ('
            with self.synchronized:
                if self.connected:
                    result += 'connected) at 0x{0:x}>'.format(self._myo.value)
                else:
                    result += 'disconnected)>'
            return result

        def __hash__(self):
            return self._myo.value

        def __assert_connected(self):
            if not self.connected:
                raise RuntimeError('Myo was disconnected')

        @property
        def connected(self):
            with self.synchronized:
                return (
                    self._connect_time is not None and
                    self._disconnect_time is None
                )

        @property
        def paired(self):
            with self.synchronized:
                return (self.myo_ is None or self._unpair_time is not None)

        @property
        def pair_time(self):
            return self._pair_time

        @property
        def unpair_time(self):
            with self.synchronized:
                return self._unpair_time

        @property
        def connect_time(self):
            return self._connect_time

        @property
        def disconnect_time(self):
            with self.synchronized:
                return self._disconnect_time

        @property
        def firmware_version(self):
            return self._firmware_version

        @property
        def orientation(self):
            with self.synchronized:
                return self._orientation.copy()

        @property
        def acceleration(self):
            with self.synchronized:
                return self._acceleration.copy()

        @property
        def gyroscope(self):
            with self.synchronized:
                return self._gyroscope.copy()

        @property
        def pose(self):
            with self.synchronized:
                return self._pose

        @property
        def arm(self):
            with self.synchronized:
                return self._arm

        @property
        def x_direction(self):
            with self.synchronized:
                return self._xdir

        @property
        def rssi(self):
            with self.synchronized:
                return self._rssi

        @property
        def emg(self):
            with self.synchronized:
                return self._emg

        def set_locking_policy(self, locking_policy):
            with self.synchronized:
                self.__assert_connected()
                self._myo.set_locking_policy(locking_policy)

        def set_stream_emg(self, emg):
            with self.synchronized:
                self.__assert_connected()
                self._myo.set_stream_emg(emg)

        def vibrate(self, vibration_type):
            with self.synchronized:
                self.__assert_connected()
                self._myo.vibrate(vibration_type)

        def request_rssi(self):
            """
            Requests the RSSI of the Myo armband. Until the RSSI is
            retrieved, :attr:`rssi` returns None.
            """

            with self.synchronized:
                self.__assert_connected()
                self._rssi = None
                self._myo.request_rssi()

    def __init__(self):
        super(Feed, self).__init__()
        self.synchronized = threading.Condition()
        self._myos = {}

    def get_devices(self):
        """
        get_devices() -> list of Feed.MyoProxy

        Returns a list of paired and connected Myo's.
        """

        with self.synchronized:
            return list(self._myos.values())

    def get_connected_devices(self):
        """
        get_connected_devices(self) -> list of Feed.MyoProxy

        Returns a list of connected Myo's.
        """

        with self.synchronized:
            return [myo for myo in self._myos.values() if myo.connected]

    def wait_for_single_device(self, timeout=None, interval=0.5):
        """
        wait_for_single_device(timeout) -> Feed.MyoProxy or None

        Waits until a Myo is was paired **and** connected with the Hub
        and returns it. If the *timeout* is exceeded, returns None.
        This function will not return a Myo that is only paired but
        not connected.

        :param timeout: The maximum time to wait for a device.
        :param interval: The interval at which the function should
            exit sleeping. We can not sleep endlessly, otherwise
            the main thread can not be exit, eg. through a
            KeyboardInterrupt.
        """

        timer = TimeoutClock(timeout)
        start = time.time()
        with self.synchronized:
            # As long as there are no Myo's connected, wait until we
            # get notified about a change.
            while not timer.exceeded:
                # Check if we found a Myo that is connected.
                for myo in six.itervalues(self._myos):
                    if myo.connected:
                        return myo

                remaining = timer.remaining
                if interval is not None and remaining > interval:
                    remaining = interval
                self.synchronized.wait(remaining)

        return None

    # DeviceListener

    def on_event(self, kind, event):
        myo = event.myo
        timestamp = event.timestamp
        with self.synchronized:
            if kind == EventType.paired:
                fmw_version = event.firmware_version
                self._myos[myo.value] = self.MyoProxy(myo, timestamp, fmw_version)
                self.synchronized.notify_all()
                return True
            elif kind == EventType.unpaired:
                try:
                    proxy = self._myos.pop(myo.value)
                except KeyError:
                    message = "Myo 0x{0:x} was not in the known Myo's list"
                    warnings.warn(message.format(myo.value), RuntimeWarning)
                else:
                    # Remove the reference handle from the Myo proxy.
                    with proxy.synchronized:
                        proxy._unpair_time = timestamp
                        proxy._myo = None
                finally:
                    self.synchronized.notify_all()
                return True
            else:
                try:
                    proxy = self._myos[myo.value]
                except KeyError:
                    message = "Myo 0x{0:x} was not in the known Myo's list"
                    warnings.warn(message.format(myo.value), RuntimeWarning)
                    return True

        with proxy.synchronized:
            if kind == EventType.connected:
                proxy._connect_time = timestamp
            elif kind == EventType.disconnected:
                proxy._disconnect_time = timestamp
            elif kind == EventType.emg:
                proxy._emg = event.emg
            elif kind == EventType.arm_synced:
                proxy._arm = event.arm
                proxy._xdir = event.x_direction
            elif kind == EventType.rssi:
                proxy._rssi = event.rssi
            elif kind == EventType.pose:
                proxy._pose = event.pose
            elif kind == EventType.orientation:
                proxy._orientation = event.orientation
                proxy._gyroscope = event.gyroscope
                proxy._acceleration = event.acceleration

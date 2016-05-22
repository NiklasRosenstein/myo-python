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

__all__ = [
    'lib',
    'ErrorDetails', 'Hub', 'Myo', 'Event', 'HandlerCallback',
    'error_details_t', 'hub_t', 'myo_t', 'event_t', 'handler_t']

from . import enums
from .exception import error, ResultError, InvalidOperation
from ..utils.platform import platform
from ..vector import Vector
from ..quaternion import Quaternion

import abc
import ctypes
import os
import six
import sys
import warnings
import traceback

from six.moves import range
from ctypes import byref, POINTER, PYFUNCTYPE, py_object
from ctypes import c_int, c_uint, c_int8, c_uint64, c_float, c_void_p, c_char_p


class MyoLibrary(object):
    """
    Wrapper for a :mod:`ctypes.CDLL` representing the Myo library.
    """

    def __init__(self):
        super(MyoLibrary, self).__init__()
        self._lib = None

    def __getattr__(self, name):
        """
        If an attribute could not be resolved on the MyoLibrary
        object itself, it is resolved on the loaded library.
        """

        if not self._lib:
            raise AttributeError(name)
        return getattr(self._lib, 'libmyo_' + name)

    def __nonzero__(self):
        """
        :return: True if the Myo library is initialized, False if not.
        """

        return self._lib is not None

    __bool__ = __nonzero__  # Python 3
    initialized = __nonzero__

    def init(self, dist_path=None):
        """
        Initializes the :class:`MyoLibrary` by detecting the name
        of the library to load with :mod:`ctypes` based on the
        current platform.

        :param dist_path: If specified, must point to the directory
            where the Myo shared library is located.
        :raise RuntimeError: If the library is already initialized.
        :raise EnvironmentError: If the current platform is not
            supported. Usually raised already by
            :mod:`myo.utils.platform`.
        :raise OSError: If the library could not be loaded.

        *Changed in 0.2.1* - Removed ``add_to_path`` parameter.
        """

        if self._lib is not None:
            raise RuntimeError('already initialized')

        # Determine the architecture so we can actually load
        # the right version of the library.
        if sys.maxsize <= 2 ** 32:
            arch = 32
        else:
            arch = 64

        # Determine the name which can be used to load the library
        # based on the current platform.
        if platform == 'Windows' or platform == 'Windows (Cygwin)':
            lib_name = 'myo%d.dll' % arch
        elif platform == 'Darwin':
            # lib name is just 'myo' as per:
            # https://developer.thalmic.com/forums/topic/541/?page=2
            lib_name = 'myo'
        else:
            raise EnvironmentError('unsupported platform %s' % platform)

        # Load the library from an absolute path if *dist_path*
        # is specified.
        if dist_path:
            dist_path = os.path.normpath(os.path.abspath(dist_path))
            lib_name = os.path.join(dist_path, lib_name)

        # Load the library. Could raise OSError.
        self._lib = ctypes.cdll.LoadLibrary(lib_name)

        # Initialize the library.
        for class_ in BaseTypeWrapper.__subclasses__():
            class_.init_libmyo(self)

    def init_func(self, name, restype, *argtypes):
        """
        Initializes the *restype* and *argtypes* of a function in
        with the specified *name* on the global :data:`lib`. ``'libmyo_'``
        is preprended to *name* as the :data:`lib` is wrapped by a
        :class:`ShortcutAccess` object.
        """

        func = getattr(self._lib, 'libmyo_' + name)
        func.restype = restype
        func.argtypes = argtypes


class BaseTypeWrapper(c_void_p):
    """
    A :class:`ctypes.c_void_p` subclass that is supposed to wrap
    a handle from the Myo SDK. A subclass has to implement a static
    method to initialize the contents of the ``libmyo`` shared library
    that it requires.
    """

    def __init__(self, *args, **kwargs):
        c_void_p.__init__(self, *args, **kwargs)

    def init_libmyo(lib):
        raise NotImplementedError

    def _notnull(self):
        """
        Raises a RuntimeError when the internal pointer is a nullptr.
        """

        if not self:
            class_name = type(self).__name__
            message = '%s object is nullptr' % class_name
            raise RuntimeError(message)

    def _memraise(self):
        """
        Should be called if a memory allocation was expected. Raises
        a MemoryError when the internal pointer is a nullptr.
        """

        if not self:
            class_name = type(self).__name__
            raise MemoryError('Could not allocate %s object.' % class_name)


class ErrorDetails(BaseTypeWrapper):
    """
    Wrapper for ``error_details_t``.
    """

    @staticmethod
    def init_libmyo(lib):
        lib.init_func('error_cstring', c_char_p, ErrorDetails)
        lib.init_func('error_kind', enums.Result, ErrorDetails)
        lib.init_func('free_error_details', None, ErrorDetails)

    def __del__(self):
        if self:
            lib.free_error_details(self)
            self.value = None

    def __repr__(self):
        if not self:
            return '<ErrorDetails nullptr>'
        return '<ErrorDetails (%s) %r>' % (self.kind.name, self.message)

    @property
    def kind(self):
        self._notnull()
        return lib.error_kind(self)

    @property
    def message(self):
        self._notnull()
        return str(lib.error_cstring(self))

    def raise_on_error(self):
        """
        Raises a :class:`ResultError` when this ``error_details_t``
        represents an errornous state. Does nothing if it does not.
        """

        if self:
            raise ResultError(self.kind, self.message)


class Hub(BaseTypeWrapper):
    """
    Lowlevel wrapper for a Myo Hub. You should never use this class
    directly and always use the high-level :class:`myo.Hub` interface
    instead.
    """

    @staticmethod
    def init_libmyo(lib):
        lib.init_func(
            'init_hub', enums.Result,
            POINTER(Hub), POINTER(ErrorDetails))
        lib.init_func(
            'shutdown_hub', enums.Result,
            Hub, POINTER(ErrorDetails))
        lib.init_func(
            'set_locking_policy', enums.Result,
            Hub, enums.LockingPolicy, POINTER(ErrorDetails))
        lib.init_func(
            'run', enums.Result,
            Hub, c_uint, HandlerCallback, py_object,
            POINTER(ErrorDetails))

    def __init__(self):
        """
        Creates a new Myo Hub object.

        :raise ResultError: If an error occured.
        :raise MemoryError: If the Hub could not be created due
            to a memory error.
        """

        super(BaseTypeWrapper, self).__init__(None)
        error = ErrorDetails()
        lib.init_hub(byref(self), byref(error))
        error.raise_on_error()
        self._memraise()

    def __del__(self):
        if self:
            warnings.warn(
                "Hub not shut down before garbage collection.",
                RuntimeWarning)
            self.shutdown()

    def run(self, duration_ms, callback, ud=None):
        """
        Runs the Hub for *duration_ms* milliseconds.

        :param duration_ms: The number f milliseconds the hub should run.
        :param callback: The callback that is invoked for each event.
        :param ud: User data that is passed to *callback*
        :return: True if the run was complete, False if *callback* caused
            the Hub to stop by returning False or if an exception
            occured.
        """

        self._notnull()

        if not isinstance(duration_ms, int):
            raise TypeError('duration_ms must be integer')
        if not callable(callback):
            raise TypeError('callback must be callable')

        # Wrapper that makes sure the callback returns the
        # right values and handles the stop-request of the
        # listener (when it returns False).
        def wrapper(ud, event):

            # Invoke the callback and process the result. It
            # should be a bool, and if it is notm we want to
            # warn the user.
            try:
                result = callback(ud, event)
            except BaseException:
                wrapper.exc_info = sys.exc_info()
                result = False

            # Warn the user if the callback did not return a
            # boolean value (we really only accept that!).
            if not isinstance(result, bool):
                n1 = callback.__name__
                n2 = result.__class__.__name__
                message = 'callback %s() should return bool, got %s'
                warnings.warn(message % (n1, n2))

            # Invalidate the event object completely. It must
            # not be used after this function has ended.
            event.value = 0

            if result:
                return enums.HandlerResult.continue_
            else:
                wrapper.stopped = True
                return enums.HandlerResult.stop

        # Run the function which will block the current thread.
        error = ErrorDetails()
        result = lib.run(self, duration_ms, HandlerCallback(wrapper),
                         ud, byref(error))
        error.raise_on_error()

        # Did an exception occur in the callback? Propagate it.
        exc_info = getattr(wrapper, 'exc_info', None)
        if exc_info:
            six.reraise(*exc_info)

        return not getattr(wrapper, 'stopped', False)

    def shutdown(self):
        """
        Shuts the Hub down if it is running. The object is not usable
        after calling this function.
        """

        if not self.value:
            return None  # already shut down
        error = ErrorDetails()
        result = lib.shutdown_hub(self, byref(error))
        self.value = None
        error.raise_on_error()
        return result

    def set_locking_policy(self, locking_policy):
        """
        Sets the myo locking policy for this Hub.

        :see also: :class:`enums.LockingPolicy`
        """

        self._notnull()
        error = ErrorDetails()
        result = lib.set_locking_policy(self, locking_policy, byref(error))
        error.raise_on_error()
        return result


class Myo(BaseTypeWrapper):
    ''' C-types wrapper for a Myo armband. '''

    @staticmethod
    def init_libmyo(lib):
        lib.init_func(
            'vibrate', enums.Result,
            Myo, enums.VibrationType, POINTER(ErrorDetails))
        lib.init_func(
            'request_rssi', enums.Result,
            Myo, POINTER(ErrorDetails))
        lib.init_func(
            'request_battery_level', enums.Result,
            Myo, POINTER(ErrorDetails))
        lib.init_func(
            'set_stream_emg', enums.Result,
            Myo, enums.StreamEmg, POINTER(ErrorDetails))
        lib.init_func(
            'myo_unlock', enums.Result,
            Myo, enums.UnlockType, POINTER(ErrorDetails))
        lib.init_func(
            'myo_lock', enums.Result,
            Myo, POINTER(ErrorDetails))
        lib.init_func(
            'myo_notify_user_action', enums.Result,
            Myo, enums.UserActionType, POINTER(ErrorDetails))

    def vibrate(self, vibration_type):
        self._notnull()
        error = ErrorDetails()
        try:
            return lib.vibrate(self, vibration_type, byref(error))
        finally:
            error.raise_on_error()

    def request_rssi(self):
        self._notnull()
        error = ErrorDetails()
        try:
            return lib.request_rssi(self, byref(error))
        finally:
            error.raise_on_error()

    def request_battery_level(self):
        self._notnull()
        error = ErrorDetails()
        try:
            return lib.request_battery_level(self, byref(error))
        finally:
            error.raise_on_error()

    def set_stream_emg(self, stream_emg):
        self._notnull()
        error = ErrorDetails()
        try:
            return lib.set_stream_emg(self, stream_emg, byref(error))
        finally:
            error.raise_on_error()

    def myo_unlock(self, unlock_type):
        self._notnull()
        error = ErrorDetails()
        try:
            return lib.myo_unlock(self, unlock_type, byref(error))
        finally:
            error.raise_on_error()

    def myo_lock(self):
        self._notnull()
        error = ErrorDetails()
        try:
            return lib.myo_lock(self, byref(error))
        finally:
            error.raise_on_error()

    def myo_notify_user_action(self, user_action_type):
        self._notnull()
        error = ErrorDetails()
        try:
            return lib.myo_notify_user_action(
                self, user_action_type, byref(error))
        finally:
            error.raise_on_error()


class Event(BaseTypeWrapper):
    """
    Represents a Myo ``event_t`` object. Not all properties can be
    accessed at all times. :class`InvalidOperation` is raised if you
    attempt to read :attr:`orientation` in any but the *orientation*
    event, and vice versa.
    """

    @staticmethod
    def init_libmyo(lib):
        lib.init_func('event_get_type', enums.EventType, Event)
        lib.init_func('event_get_timestamp', c_uint64, Event)
        lib.init_func('event_get_myo', Myo, Event)
        lib.init_func('event_get_firmware_version', c_uint,
                      Event, enums.VersionComponent)
        lib.init_func('event_get_arm', enums.Arm, Event)
        lib.init_func('event_get_x_direction', enums.XDirection, Event)
        lib.init_func('event_get_warmup_state', enums.WarmupState, Event)
        lib.init_func('event_get_warmup_result', enums.WarmupResult, Event)
        lib.init_func('event_get_rotation_on_arm', c_float, Event)
        lib.init_func('event_get_orientation', c_float,
                      Event, enums.OrientationIndex)
        lib.init_func('event_get_accelerometer', c_float,
                      Event, c_uint)
        lib.init_func('event_get_gyroscope', c_float,
                      Event, c_uint)
        lib.init_func('event_get_pose', enums.Pose, Event)
        lib.init_func('event_get_rssi', c_int8, Event)
        lib.init_func('event_get_battery_level', c_int8, Event)
        lib.init_func('event_get_emg', c_int8, Event, c_uint)

    def _checktype(self, current_op, *types):
        """
        Ensures that the event *self* is of one of the specified events
        in *\*types*.

        :param current_op: A string that identifies the attempted operation.
        :raise InvalidOperation: If it is not the case.
        """

        self._notnull()

        # Check if one of the *types are the same as the actual event type.
        found = False
        self_type = self.type
        for type_ in types:
            if type_ == self_type:
                found = True
                break

        if not found:
            message = 'operation `%s` not allowed in `%s` event'
            raise InvalidOperation(message % (current_op, self_type.name))

    @property
    def type(self):
        """
        type -> enums.EventType

        Returns the type of the event. Can be accessed at all events.
        """

        self._notnull()
        return lib.event_get_type(self)

    @property
    def timestamp(self):
        """
        timestamp -> long

        Returns the timestamp of the event. Can be accessed at all events.
        """

        self._notnull()
        return lib.event_get_timestamp(self)

    @property
    def myo(self):
        """
        myo -> Myo

        Returns the Myo of the event. Can be accessed at all events.
        """

        self._notnull()
        return lib.event_get_myo(self)

    @property
    def firmware_version(self):
        """
        firmware_version -> (major, minor, patch)

        Returns the firmware version. Can only be called from a
        *paired* and *connected* event
        """

        self._checktype(
            'get firmware_version',
            enums.EventType.paired, enums.EventType.connected)
        major = lib.event_get_firmware_version(self, enums.VersionComponent.major)
        minor = lib.event_get_firmware_version(self, enums.VersionComponent.minor)
        patch = lib.event_get_firmware_version(self, enums.VersionComponent.patch)
        return (major, minor, patch)

    @property
    def arm(self):
        """
        arm -> enums.Arm

        Returns the arm the Myo is put on. Can only be called on an
        *arm_synced* event.
        """

        self._checktype('get arm', enums.EventType.arm_synced)
        return lib.event_get_arm(self)

    @property
    def x_direction(self):
        """
        x_direction -> enums.XDirection

        Returns the X direction of the Myo. Can only be called on an
        *arm_synced* event.
        """

        self._checktype('get x direction', enums.EventType.arm_synced)
        return lib.event_get_x_direction(self)

    @property
    def warmup_state(self):
        """
        warmup_state -> enums.WarmupState

        Returns the warmup state of the Myo. Can only be called on an
        *arm_synced* event.
        """

        self._checktype('get warmup state', enums.EventType.arm_synced)
        return lib.event_get_warmup_state(self)

    @property
    def warmup_result(self):
        """
        warmup_result -> enums.WarmupResult

        Returns the warmup result of the Myo. Can only be called on an
        *warmup_completed* event.
        """

        self._checktype('get warmup result', enums.EventType.warmup_completed)
        return lib.event_get_warmup_result(self)

    @property
    def rotation(self):
        """
        rotation -> float

        Returns the rotation on arm. Can only be called on an
        *arm_synced* event.
        """

        self._checktype('get rotation', enums.EventType.arm_synced)
        return lib.event_get_rotation_on_arm(self)

    @property
    def orientation(self):
        """
        orientation -> Quaternion

        Returns the acceleration :class:`myo.quaternion.Quaternion` for
        this event. Can only be called from the *orientation* event.
        """

        self._checktype('get orientation', enums.EventType.orientation)
        return Quaternion(
            lib.event_get_orientation(self, enums.OrientationIndex.x),
            lib.event_get_orientation(self, enums.OrientationIndex.y),
            lib.event_get_orientation(self, enums.OrientationIndex.z),
            lib.event_get_orientation(self, enums.OrientationIndex.w))

    @property
    def acceleration(self):
        """
        acceleration -> Vector

        Returns the acceleration :class:`myo.vector.Vector` for this
        event. Can only be called from the *orientation* event.
        """

        self._checktype('get acceleration', enums.EventType.orientation)
        return Vector(
            lib.event_get_accelerometer(self, 0),
            lib.event_get_accelerometer(self, 1),
            lib.event_get_accelerometer(self, 2))

    @property
    def gyroscope(self):
        """
        gyroscope -> Vector

        Returns the gyroscope :class:`myo.vector.Vector` for this
        event. Can only be called from the *orientation* event.
        """

        self._checktype('get gyroscope', enums.EventType.orientation)
        return Vector(
            lib.event_get_gyroscope(self, 0),
            lib.event_get_gyroscope(self, 1),
            lib.event_get_gyroscope(self, 2))

    @property
    def pose(self):
        """
        pose -> enums.Pose

        Returns the pose of the event. Can only be called from a
        *pose* event.
        """

        self._checktype('get pose', enums.EventType.pose)
        return lib.event_get_pose(self)

    @property
    def rssi(self):
        """
        rssi -> int (8)

        Returns the RSSI. Can only be called from an *rssi* event.
        """

        self._checktype('get rssi', enums.EventType.rssi)
        return lib.event_get_rssi(self)

    @property
    def level(self):
        """
        level -> int (8)

        Returns the battery level. Can only be called from an
        *bettery_level* event.
        """

        self._checktype('get battery level', enums.EventType.bettery_level)
        return lib.event_get_battery_level(self)

    @property
    def emg(self):
        """
        emg -> tuple of 8 ints

        Returns the EMG data on an *emg* event.
        """

        self._checktype('get emg', enums.EventType.emg)
        return tuple(lib.event_get_emg(self, i) for i in range(8))


# Callback function type for libmyo_run(). hub_t.run() expects
# a slightly different interface.
HandlerCallback = PYFUNCTYPE(c_int, py_object, Event)

# Backwards compatibility
error_details_t = ErrorDetails
hub_t = Hub
myo_t = Myo
event_t = Event
handler_t = HandlerCallback

# The globally loaded MyoLibrary. Todo: It would be nice if it was not
# global but could just be created on a local level and all contents be
# accessed through it.
lib = MyoLibrary()

# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.
r"""
myo.lowlevel - Lowlevel Myo SDK interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

__all__ = (
    # enumerations
    'result_t', 'vibration_type_t', 'pose_t', 'event_type_t',
    'version_component_t', 'orientation_index_t', 'handler_result_t',

    # structure wrappers
    'error_details_t', 'hub_t', 'myo_t',
    # REMOVED IN 0.8.6.2 'training_dataset_t',
    'event_t',

    # callback types
    # REMOVED IN 0.8.6.2 'training_collect_status_t',
    'handler_t',

    # exceptions
    'MyoError', 'ResultError', 'InvalidOperation',

    # functions
    'init', 'initialized', 
    # REMOVED IN 0.8.6.2 'now',
)

import os
import sys
import warnings
import traceback

import ctypes
from ctypes import byref, POINTER as asptr, PYFUNCTYPE as py_functype

from myo import six
from myo.enum import Enumeration, Data as Enumeration_Data
from myo.tools import ShortcutAccess, MacAddress
from myo.platform import platform


class _Uninitialized(object):
    r""" Datatype used as the pre-init state for the internal
    shared library handle that raises an exception as soon as
    it is tried to be used. """

    def __getattribute__(self, name):
        message = 'Call myo.init() before using any SDK contents...'
        raise RuntimeError(message)

lib = _Uninitialized()

initializers = []

def is_initializer(type_):
    r""" Decorator for classes that provide an ``_init_lib()``
    static method which is called when the :mod:`myo.lowlevel`
    module is initialized to initialize the contents of :data:`lib`. """

    assert hasattr(type_, '_init_lib')
    assert callable(type_._init_lib)
    initializers.append(type_)

    return type_

def init_func(name, restype, *argtypes):
    r""" Initializes the *restype* and *argtypes* of a function in
    with the specified *name* on the global :data:`lib`. ``'libmyo_'``
    is preprended to *name* as the :data:`lib` is wrapped by a
    :class:`ShortcutAccess` object. """

    func = getattr(lib, name)
    func.restype = restype
    func.argtypes = argtypes


def init(dist_path=None, add_to_path=True):
    r""" Determines which myo shared library to load and does so.
    If *dist_path* is given, it must be the parent directory of
    the myo library to load. When *add_to_path* is True in that
    case, the ``PATH`` environment variable will be extended by
    that path. """

    global lib
    if not isinstance(lib, _Uninitialized):
        raise RuntimeError('already initialized')

    # Determine the architecture so we can actually load
    # the right version of the library.
    if sys.maxsize <= 2 ** 32:
        arch = 32
    else:
        arch = 64

    # Determine the name which can be used to load the library
    # based on the current platform.
    if platform == 'Windows':
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

        # Extend the PATH variable if that is desired.
        if add_to_path:
            PATH = os.environ['PATH']
            os.environ['PATH'] = os.pathsep.join([dist_path, PATH])

        # Or create an absolute filename.
        else:
            lib_name = os.path.join(dist_path, lib_name)

    # Load the library and initialize the required contents.
    try:
        lib = ctypes.cdll.LoadLibrary(lib_name)
    except OSError:
        sys.stderr.write('Error loading "%s". Make sure that it is in your path.\n' % lib_name)
        raise

    lib = ShortcutAccess(lib, 'libmyo_')

    for class_ in initializers:
        class_._init_lib()

    # Initialize global library functions.
    # REMOVED IN 0.8.6.2 init_func('now', ctypes.c_uint64)

def initialized():
    r""" Returns True if :meth:`init` has been called successfully
    already, False if not. """

    return not isinstance(lib, _Uninitialized)


class result_t(Enumeration):

    success = 0
    error = 1
    error_invalid_argument = 2
    error_runtime = 3

    __fallback__ = -1

class vibration_type_t(Enumeration):

    short = 0
    medium = 1
    long = 2

    __fallback__ = -1

class stream_emg(Enumeration):

    # Do not send EMG data.
    disabled = 0
    # Send EMG data.
    enabled = 1

    __fallback__ = -1

class pose_t(Enumeration):

    rest = 0
    fist = 1
    wave_in = 2
    wave_out = 3
    fingers_spread = 4
    double_tap = 5

    __fallback__ = -1
    num_poses = Enumeration_Data(6)

class event_type_t(Enumeration):

    paired = 0
    # beta 3
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

    __fallback__ = -1

class version_component_t(Enumeration):

    major = 0
    minor = 1
    patch = 2

    __fallback__ = -1

class orientation_index_t(Enumeration):

    x = 0
    y = 1
    z = 2
    w = 3

    __fallback__ = -1

class handler_result_t(Enumeration):

    continue_ = 0
    stop = 1

    __fallback__ = -1

#Locking policy added in beta7

class locking_policy_t(Enumeration):
    none = 0    # Pose events are always sent.
    standard =1 # (default) Pose events are not sent while a Myo is locked.

    __fallback__ = -1

class arm_t(Enumeration):

    right = 0
    left = 1
    unknown = 2

    __fallback__ = -1

class x_direction_t(Enumeration):

    toward_wrist = 0
    toward_elbow = 1
    unknown = 2

    __fallback__ = -1

class base_void_p(ctypes.c_void_p):
    r""" Base class for the Myo void\* pointer types which implements
    a few convenience methods to check for nullptr and even automatically
    raising a MemoryError. """

    def _notnull(self):
        r""" Protected. Raises a RuntimeError when the internal pointer
        is a nullptr. """

        if not self:
            class_name = self.__class__.__name__
            message = '%s object is a nullptr' % class_name
            raise RuntimeError(message)

    def _memraise(self):
        r""" Raises a MemoryError when the internal pointer is a nullptr
        as a successful memory allocation was expected. """

        if not self:
            class_name = self.__class__.__name__
            raise MemoryError('Could not allocate %s object. Make sure that Myo Connect is running and a Myo is paired.' % class_name)

@is_initializer
class error_details_t(base_void_p):

    @staticmethod
    def _init_lib():
        init_func('error_cstring', ctypes.c_char_p, error_details_t)
        init_func('error_kind', result_t, error_details_t)
        init_func('free_error_details', None, error_details_t)

    def __del__(self):
        if self:
            lib.free_error_details(self)
            self.value = None

    def __repr__(self):
        if not self:
            return '<error_details_t nullptr>'
        return '<error_details_t (%s) %r>' % (self.kind.name, self.message)

    @property
    def kind(self):
        self._notnull()
        return lib.error_kind(self)

    @property
    def message(self):
        self._notnull()
        return str(lib.error_cstring(self))

    def raise_on_error(self):
        r""" Raises a :class:`error` when this error_details_t
        represents an errornous state. Does nothing if it does not. """

        if self:
            raise ResultError(self.kind, self.message)

@is_initializer
class hub_t(base_void_p):

    @staticmethod
    def _init_lib():
        init_func('init_hub', result_t,
                asptr(hub_t), asptr(error_details_t))
        # libmyo_result_t libmyo_shutdown_hub(libmyo_hub_t hub, libmyo_error_details_t* out_error);
        init_func('shutdown_hub', result_t,
                hub_t, asptr(error_details_t))
        #Added in beta 7
        init_func('set_locking_policy', result_t, hub_t, locking_policy_t, asptr(error_details_t) )

# REMOVED IN 0.8.6.2
#         init_func('pair_any', result_t,
#                 hub_t, ctypes.c_uint, asptr(error_details_t))
#         init_func('pair_by_mac_address', result_t,
#                 hub_t, ctypes.c_uint64, asptr(error_details_t))
#         init_func('pair_adjacent', result_t,
#                 hub_t, ctypes.c_uint, asptr(error_details_t))
        init_func('run', result_t,
                hub_t, ctypes.c_uint, handler_t, ctypes.py_object, error_details_t)

    @staticmethod
    def init_hub():
        r""" Creates a new hub_t object and returns it. Raises a
        :class:`ResultError` when an error occurred. """

        hub = hub_t()
        error = error_details_t()
        lib.init_hub(byref(hub), byref(error))
        error.raise_on_error()
        hub._memraise()
        return hub

    def shutdown(self):
        r""" Shuts the hub down. The object is not usable after
        calling this function. """

        self._notnull()
        error = error_details_t()
        result = lib.shutdown_hub(self, byref(error))
        self.value = None
        error.raise_on_error()
        return result

    def set_locking_policy(self, locking_policy):
        r""" Sets the myo locking policy (see locking_policy_t enumeration)"""
        
        self._notnull()
        error = error_details_t()
        result = lib.set_locking_policy(self, locking_policy, byref(error))
        error.raise_on_error()
        return result

    def pair_any(self, n=1):
        r""" Pairs with any *n* devices. The device listener will
        receive the connection events. """

        self._notnull()
        if n <= 0:
            raise ValueError('n must be a non-zero positive number')

        error = error_details_t()
        result = lib.pair_any(self, n, byref(error))
        error.raise_on_error()
        return result

    @DeprecationWarning
    def pair_by_mac_address(self, mac_address):
        r""" Pairs with a Myo of a specific *mac_address*. The
        address can be either an integer representing the mac
        address or a string. """

        self._notnull()
        mac_address = MacAddress(mac_address)

        error = error_details_t()
        result = lib.pair_by_mac_address(self, mac_address.intval, byref(error))
        error.raise_on_error()
        return result

    @DeprecationWarning
    def pair_adjacent(self, n=1):
        r""" Pair with *n* adjacent devices. """

        self._notnull()
        if n <= 0:
            raise ValueError('n must be a non-zero positive number')

        error = error_details_t()
        result = lib.pair_adjacent(self, n, byref(error))
        error.raise_on_error()
        return result

    def run(self, duration_ms, callback, ud=None):
        r""" Runs the hub for *duration_ms* milliseconds and invokes
        *callback* for events. It must be a callable object which accepts
        *ud* and a :class:`event_t` object. When the *callback* returns
        True, it signals the hub that is should continue to process
        events. If it returns False, it will not continue to process
        events.

        This function returns True if the run was complete, False
        if the *callback* caused the Hub to stop by returning False. """

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
            except Exception:
                traceback.print_exc()
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
                return handler_result_t.continue_
            else:
                wrapper.stopped = True
                return handler_result_t.stop

        # Run the function which will block the current thread.
        error = error_details_t()
        result = lib.run(self, duration_ms, handler_t(wrapper), ud, byref(error))
        error.raise_on_error()

        # Return True if the run was complete, meaning the callback
        # did not request to halt the Hub.
        return not getattr(wrapper, 'stopped', False)

    def __del__(self):
        if self:
            self.shutdown()

@is_initializer
class myo_t(base_void_p):

    @staticmethod
    def _init_lib():
        # REMOVED IN 0.8.6.2
        #init_func('get_mac_address', ctypes.c_uint64, myo_t)
        init_func('vibrate', result_t,
                myo_t, vibration_type_t, asptr(error_details_t))
        init_func('request_rssi', result_t, myo_t, asptr(error_details_t))
        init_func('set_stream_emg', result_t, myo_t, stream_emg, asptr(error_details_t))
        # REMOVED IN 0.8.6.2
        #init_func('training_is_available', ctypes.c_int, myo_t)
        #init_func('training_load_profile', result_t,
        #        myo_t, ctypes.c_char_p, asptr(error_details_t))

    @property
    def mac_address(self):
        self._notnull()
        return MacAddress(lib.get_mac_address(self))

    def vibrate(self, vibration_type):
        self._notnull()
        error = error_details_t()
        try:
            return lib.vibrate(self, vibration_type, byref(error))
        finally:
            error.raise_on_error()

    def request_rssi(self):
        self._notnull()
        error = error_details_t()
        try:
            return lib.request_rssi(self, byref(error))
        finally:
            error.raise_on_error()

    def set_stream_emg(self, emg):
        self._notnull()
        error = error_details_t()
        try:
            return lib.set_stream_emg(self, emg, byref(error))
        finally:
            error.raise_on_error()

    def training_load_profile(self, filename=None):
        self._notnull()
        error = error_details_t()
        try:
            return lib.training_load_profile(self, filename, byref(error))
        finally:
            error.raise_on_error()

    @property
    def training_is_available(self):
        self._notnull()
        return lib.training_is_available(self) != 0

@DeprecationWarning
@is_initializer
class training_dataset_t(base_void_p):

    @staticmethod
    def _init_lib():
# REMOVED IN 0.8.6.2
#         init_func('training_create_dataset', result_t,
#                 myo_t, asptr(training_dataset_t), asptr(error_details_t))
#         init_func('training_collect_data', result_t,
#                 training_dataset_t, pose_t, training_collect_status_t,
#                 base_void_p, asptr(error_details_t))
#         init_func('training_train_from_dataset', result_t,
#                 training_dataset_t, asptr(error_details_t))
#         init_func('training_free_dataset', None, training_dataset_t)
#         init_func('training_store_profile', result_t,
#                 myo_t, ctypes.c_char_p, asptr(error_details_t))
#         init_func('training_send_training_data', result_t,
#                 training_dataset_t, asptr(error_details_t))
#         init_func('training_annotate_training_data', result_t,
#                 training_dataset_t, ctypes.c_char_p, ctypes.c_char_p,
#                 asptr(error_details_t))
        pass

@is_initializer
class event_t(base_void_p):

    @staticmethod
    def _init_lib():
        init_func('event_get_type', event_type_t, event_t)
        init_func('event_get_timestamp', ctypes.c_uint64, event_t)
        init_func('event_get_myo', myo_t, event_t)
        init_func('event_get_firmware_version', ctypes.c_uint,
                event_t, version_component_t)
        init_func('event_get_orientation', ctypes.c_float,
                event_t, orientation_index_t)
        init_func('event_get_accelerometer', ctypes.c_float,
                event_t, ctypes.c_uint)
        init_func('event_get_gyroscope', ctypes.c_float,
                event_t, ctypes.c_uint)
        init_func('event_get_pose', pose_t, event_t)
        init_func('event_get_rssi', ctypes.c_int8, event_t)
        init_func('event_get_emg', ctypes.c_int8, event_t, ctypes.c_uint)
        init_func('event_get_arm', arm_t, event_t)
        init_func('event_get_x_direction', x_direction_t, event_t)

    def _checktype(self, current_op, *types):
        r""" Ensures that the event *self* is of one of the specified
        event *\*types*. Raises an InvalidOperation exception if it is
        not the case. *current_op* is a string that identifies the
        attempted operation. """

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
        self._notnull()
        return lib.event_get_type(self)

    @property
    def timestamp(self):
        self._notnull()
        return lib.event_get_timestamp(self)

    @property
    def myo(self):
        self._notnull()
        return lib.event_get_myo(self)

    @property
    def firmware_version(self):
        self._checktype('get firmware_version',
                event_type_t.paired, event_type_t.connected)
        major = lib.event_get_firmware_version(self, version_component_t.major)
        minor = lib.event_get_firmware_version(self, version_component_t.minor)
        patch = lib.event_get_firmware_version(self, version_component_t.patch)
        return (major, minor, patch)

    @property
    def orientation(self):
        self._checktype('get orientation', event_type_t.orientation)
        return [lib.event_get_orientation(self, i) for i in orientation_index_t]

    @property
    def acceleration(self):
        self._checktype('get acceleration', event_type_t.orientation)
        return [lib.event_get_accelerometer(self, i) for i in six.range(3)]

    @property
    def gyroscope(self):
        self._checktype('get gyroscope', event_type_t.orientation)
        return [lib.event_get_gyroscope(self, i) for i in six.range(3)]

    @property
    def pose(self):
        self._checktype('get pose', event_type_t.pose)
        return lib.event_get_pose(self)

    @property
    def rssi(self):
        self._checktype('get rssi', event_type_t.rssi)
        return lib.event_get_rssi(self)

    @property
    def emg(self):
        self._checktype('get emg', event_type_t.emg)
        return [lib.event_get_emg(self, i) for i in six.range(8)]

    @property
    def arm(self):
        self._checktype('get arm', event_type_t.arm_synced)
        return lib.event_get_arm(self)

    @property
    def x_direction(self):
        self._checktype('get x direction', event_type_t.arm_synced)
        return lib.event_get_x_direction(self)

def now():
    r""" Returns the current timestamp. """

    return lib.now()


# Callback function for the training_collect_data(). The
# training_dataset_t.collect_data() expects a slightly different interface.
training_collect_status_t = py_functype(None, ctypes.c_uint8, ctypes.c_uint8)

# Callback function type for libmyo_run(). hub_t.run() expects
# a slightly different interface.
handler_t = py_functype(ctypes.c_int, ctypes.py_object, event_t)


class MyoError(Exception):
    pass

class ResultError(MyoError):

    def __init__(self, kind, message):
        super(ResultError, self).__init__()
        self.kind = kind
        self.message = message

    def __str__(self):
        return str((self.kind, self.message))

class InvalidOperation(MyoError):
    pass


# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.

import os
import sys
import warnings
import traceback
from platform import platform

import ctypes
from ctypes import byref, POINTER as asptr, CFUNCTYPE as c_functype, \
        PYFUNCTYPE as py_functype

from myo import six
from myo.enum import Enumeration
from myo.tools import ShortcutAccess, macaddr_to_int


class _Uninitialized(object):
    r""" Datatype used as the pre-init state for the internal
    shared library handle that raises an exception as soon as
    it is tried to be used. """

    def __getattribute__(self, name):
        message = 'you forgot to call myo.init(), dum\'ass...'
        raise RuntimeError(message)

lib = _Uninitialized()

initializers = []

def initializer(type_):
    r""" Decorator for classes that provide an ``_init_lib()``
    static method which is called when the :mod:`myo._extern`
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

def init(dest_path=None, add_to_path=True):
    r""" Determines which myo shared library to load and does so.
    If *dest_path* is given, it must be the parent directory of
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
    if os.name == 'nt' or platform().startswith('Windows'):
        lib_name = 'myo%d.dll' % arch
    elif platform().startswith('Darwin'):
        lib_name = 'myo.dylib'
        if arch == 64:
            lib_name += '64'
    elif os.name == 'posix':
        lib_name = 'myo.so'
        if arch == 64:
            lib_name += '64'
    else:
        raise EnvironmentError('unsupported platform %s' % platform())

    # Load the library from an absolute path if *dest_path*
    # is specified.
    if dest_path:
        dest_path = os.path.normpath(os.path.abspath(dest_path))

        # Extend the PATH variable if that is desired.
        if add_to_path:
            PATH = os.environ['PATH']
            os.environ['PATH'] = os.pathsep.join([dest_path, PATH])

        # Or create an absolute filename.
        else:
            lib_name = os.path.join(dest_path, lib_name)

    # Load the library and initialize the required contents.
    lib = ctypes.cdll.LoadLibrary(lib_name)
    lib = ShortcutAccess(lib, 'libmyo_')

    for class_ in initializers:
        class_._init_lib()


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

class pose_t(Enumeration):

    none = 0
    fist = 1
    wave_in = 2
    wave_out = 3
    fingers_spread = 4
    twist_in = 5

    __fallback__ = -1
    num_poses = Enumeration.Data(6)

class event_type_t(Enumeration):

    paired = 0
    connected = 1
    disconnected = 2
    orientation = 3
    pose = 4
    rssi = 5

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


class base_void_p(ctypes.c_void_p):

    def _notnull(self):
        if not self:
            class_name = self.__class__.__name__
            message = '%s object is a nullptr' % class_name
            raise RuntimeError(message)

    def _memraise(self):
        if not self:
            class_name = self.__class__.__name__
            raise MemoryError('could not allocated %s object' % class_name)

@initializer
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

@initializer
class hub_t(base_void_p):

    @staticmethod
    def _init_lib():
        init_func('init_hub', result_t,
                asptr(hub_t), asptr(error_details_t))
        init_func('shutdown_hub', result_t,
                hub_t, asptr(error_details_t))
        init_func('pair_any', result_t,
                hub_t, ctypes.c_uint, asptr(error_details_t))
        init_func('pair_by_mac_address', result_t,
                hub_t, ctypes.c_uint64, asptr(error_details_t))
        init_func('pair_adjacent', result_t,
                hub_t, ctypes.c_uint, asptr(error_details_t))
        init_func('run', result_t,
                hub_t, ctypes.c_uint, handler_t, ctypes.py_object, error_details_t)

    @staticmethod
    def init_hub():
        r""" Creates a new hub_t object and returns it. Raises an
        :class:`error` when an error occurred. """

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

    def pair_by_mac_address(self, mac_address):
        r""" Pairs with a Myo of a specific *mac_address*. The
        address can be either an integer representing the mac
        address or a string. """

        self._notnull()
        if isinstance(mac_address, six.string_types):
            mac_address = macaddr_to_int(mac_address)
        elif not isinstance(mac_address, int):
            raise TypeError('expected string or int for mac_address')

        error = error_details_t()
        result = lib.pair_by_mac_address(self, mac_address, byref(error))
        error.raise_on_error()
        return result

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
        events. """

        self._notnull()

        if not isinstance(duration_ms, int):
            raise TypeError('duration_ms must be integer')
        if not callable(callback):
            raise TypeError('callback must be callable')

        # Wrapper that makes sure the callback returns the
        # right values,
        def wrapper(ud, event):

            # Invoke the callback and process the result. It
            # should be a bool, and if it is notm we want to
            # warn the user.
            try:
                result = callback(ud, event)
            except Exception:
                traceback.print_exc()
                return handler_result_t.stop

            if not isinstance(result, bool):
                n1 = callback.__name__
                n2 = result.__class__.__name__
                message = 'callback %s() should return bool, got %s' % (n1, n2)
                warnings.warn(message)

            if result:
                return handler_result_t.continue_
            else:
                return handler_result_t.stop

        # Run the function.
        error = error_details_t()
        result = lib.run(self, duration_ms, handler_t(wrapper), ud, byref(error))
        error.raise_on_error()
        return result

    def __del__(self):
        if self:
            self.shutdown()

@initializer
class string_t(base_void_p):

    @staticmethod
    def _init_lib():
        init_func('string_c_str', ctypes.c_char_p, string_t)
        init_func('string_free', None, string_t)

@initializer
class myo_t(base_void_p):

    @staticmethod
    def _init_lib():
        init_func('get_mac_address', ctypes.c_uint64, myo_t)
        init_func('vibrate', result_t,
                myo_t, vibration_type_t, asptr(error_details_t))
        init_func('request_rssi', result_t, myo_t, asptr(error_details_t))
        init_func('training_is_available', ctypes.c_int, myo_t)

@initializer
class training_dataset_t(base_void_p):

    @staticmethod
    def _init_lib():
        init_func('training_create_dataset', result_t,
                myo_t, asptr(training_dataset_t), asptr(error_details_t))
        init_func('training_collect_data', result_t,
                training_dataset_t, pose_t, training_collect_status_t,
                base_void_p, asptr(error_details_t))
        init_func('training_train_from_dataset', result_t,
                training_dataset_t, asptr(error_details_t))
        init_func('training_free_dataset', None, training_dataset_t)
        init_func('training_load_profile', result_t,
                myo_t, ctypes.c_char_p, asptr(error_details_t))
        init_func('training_store_profile', result_t,
                myo_t, ctypes.c_char_p, asptr(error_details_t))
        init_func('training_send_training_data', result_t,
                training_dataset_t, asptr(error_details_t))
        init_func('training_annotate_training_data', result_t,
                training_dataset_t, ctypes.c_char_p, ctypes.c_char_p,
                asptr(error_details_t))

@initializer
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

    def _checktype(self, *types):
        self._notnull()

        # Check if one of the *types are the same as the
        # actual event type.
        found = False
        self_type = self.type
        for type_ in types:
            if type_ == self_type:
                found = True
                break

        if not found:
            # todo: nice error message
            raise InvalidOperation()

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
        self._checktype(event_type_t.paired, event_type_t.connected)
        major = lib.event_get_firmware_version(self, firmware_version_t.major)
        minor = lib.event_get_firmware_version(self, firmware_version_t.minor)
        patch = lib.event_get_firmware_version(self, firmware_version_t.patch)
        return (mahor, minor, patch)

    @property
    def orientation(self):
        self._checktype(event_type_t.orientation)
        return [lib.event_get_orientation(self, i) for i in orientation_index_t]

    @property
    def accelerometer(self):
        self._checktype(event_type_t.orientation)
        return [lib.event_get_accelerometer(self, i) for i in xrange(3)]

    @property
    def gyroscope(self):
        self._checktype(event_type_t.orientation)
        return [lib.event_get_gyroscope(self, i) for i in xrange(3)]

    @property
    def pose(self):
        self._checktype(event_type_t.pose)
        return lib.event_get_pose(self)

    @property
    def rssi(self):
        self._checktype(event_type_t.rssi)
        return lib.event_get_rssi(self)

training_collect_status_t = c_functype(None, ctypes.c_uint8, ctypes.c_uint8)
handler_t = py_functype(ctypes.c_int, ctypes.py_object, event_t)


class MyoError(Exception):
    pass

class ResultError(MyoError):

    def __init__(self, kind, message):
        super(error, self).__init__()
        self.kind = kind
        self.message = message

    def __str__(self):
        return str((self.kind, self.message))

class InvalidOperation(MyoError):
    pass


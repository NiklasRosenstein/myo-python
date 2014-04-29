# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.

import os
import sys
from platform import platform

import ctypes
from ctypes import byref, POINTER as asptr, CFUNCTYPE as c_functype

from myo.enum import Enumeration


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
    is preprended to *name*. """

    func = getattr(lib, 'libmyo_' + name)
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


@initializer
class error_details_t(ctypes.c_void_p):

    @staticmethod
    def _init_lib():
        init_func('error_cstring', ctypes.c_char_p, error_details_t)
        init_func('error_kind', result_t, error_details_t)
        init_func('free_error_details', None, error_details_t)

@initializer
class hub_t(ctypes.c_void_p):

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

@initializer
class string_t(ctypes.c_void_p):

    @staticmethod
    def _init_lib():
        init_func('string_c_str', ctypes.c_char_p, string_t)
        init_func('string_free', None, string_t)

@initializer
class myo_t(ctypes.c_void_p):

    @staticmethod
    def _init_lib():
        init_func('get_mac_address', ctypes.c_uint64, myo_t)
        init_func('vibrate', result_t,
                myo_t, vibration_type_t, asptr(error_details_t))
        init_func('request_rssi', result_t, myo_t, asptr(error_details_t))
        init_func('training_is_available', ctypes.c_int, myo_t)

@initializer
class training_dataset_t(ctypes.c_void_p):

    @staticmethod
    def _init_lib():
        init_func('training_create_dataset', result_t,
                myo_t, asptr(training_dataset_t), asptr(error_details_t))
        init_func('training_collect_data', result_t,
                training_dataset_t, pose_t, training_collect_status_t,
                ctypes.c_void_p, asptr(error_details_t))
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
class event_t(ctypes.c_void_p):

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


training_collect_status_t = c_functype(None, ctypes.c_uint8, ctypes.c_uint8)
handler_t = c_functype(handler_result_t, ctypes.c_void_p, event_t)


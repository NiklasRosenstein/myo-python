# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.

import os
import sys
import ctypes

from myo.enum import Enumeration


class result_t(Enumeration):

    success = 0
    error = 1
    error_invalid_argument = 2
    error_runtime = 3

    __fallback__ = -1

class vibration_t(Enumeration):

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


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
    'Result', 'VibrationType', 'StreamEmg', 'Pose', 'EventType',
    'VersionComponent', 'OrientationIndex', 'HandlerResult', 'LockingPolicy',
    'Arm', 'XDirection', 'UnlockType', 'UserActionType', 'WarmupState', 'WarmupResult',

    # Backwards compatibility
    'result_t', 'vibration_type_t', 'stream_emg', 'pose_t', 'event_type_t',
    'version_component_t', 'orientation_index_t', 'handler_result_t',
    'locking_policy_t', 'arm_t', 'x_direction_t']


from ..utils.enum import Enumeration


class Result(Enumeration):
    ''' Enumeration for the result of an operation. '''

    success = 0
    error = 1
    error_invalid_argument = 2
    error_runtime = 3
    __fallback__ = True


class VibrationType(Enumeration):
    short = 0
    medium = 1
    long = 2
    __fallback__ = True


class StreamEmg(Enumeration):
    disabled = 0
    enabled = 1
    __fallback__ = True


class Pose(Enumeration):
    rest = 0
    fist = 1
    wave_in = 2
    wave_out = 3
    fingers_spread = 4
    double_tap = 5
    __fallback__ = True
    num_poses = Enumeration.Data(6)


class EventType(Enumeration):
    paired = 0
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
    bettery_level = 12
    warmup_completed = 13
    __fallback__ = True


class VersionComponent(Enumeration):
    major = 0
    minor = 1
    patch = 2
    __fallback__ = True


class OrientationIndex(Enumeration):
    x = 0
    y = 1
    z = 2
    w = 3
    __fallback__ = True


class HandlerResult(Enumeration):
    ''' Result of an event handler. '''

    continue_ = 0
    stop = 1
    __fallback__ = True


class LockingPolicy(Enumeration):
    ''' Policy for locking. '''

    none = 0      #: Pose events are always sent.
    standard = 1  #: (default) Pose events are not sent while a Myo is locked.
    __fallback__ = True


class Arm(Enumeration):
    right = 0
    left = 1
    unknown = 2
    __fallback__ = True


class XDirection(Enumeration):
    toward_wrist = 0
    toward_elbow = 1
    unknown = 2
    __fallback__ = True


class UnlockType(Enumeration):
    timed = 0
    hold = 1
    __fallback__ = True


class UserActionType(Enumeration):
    single = 0
    __fallback__ = True


class WarmupState(Enumeration):
    unknown = 0
    cold = 1
    warm = 2
    __fallback__ = True


class WarmupResult(Enumeration):
    unknown = 0
    success = 1
    failed_timeout = 2
    __fallback__ = True


# Backwards compatibility
result_t = Result
vibration_type_t = VibrationType
stream_emg = StreamEmg
pose_t = Pose
event_type_t = EventType
version_component_t = VersionComponent
orientation_index_t = OrientationIndex
handler_result_t = HandlerResult
locking_policy_t = LockingPolicy
arm_t = Arm
x_direction_t = XDirection

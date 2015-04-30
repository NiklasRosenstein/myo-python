// Copyright (C) 2013-2014 Thalmic Labs Inc.
// Distributed under the Myo SDK license agreement. See LICENSE.txt for details.
#pragma once

#include <stdint.h>

#include "Pose.hpp"

namespace myo {

class Myo;
template<typename T>
class Quaternion;
template<typename T>
class Vector3;

/// Enumeration identifying a right arm or left arm.
enum Arm {
    armLeft = libmyo_arm_left,
    armRight = libmyo_arm_right,
    armUnknown = libmyo_arm_unknown
};

/// Possible directions for Myo's +x axis relative to a user's arm.
enum XDirection {
    xDirectionTowardWrist = libmyo_x_direction_toward_wrist,
    xDirectionTowardElbow = libmyo_x_direction_toward_elbow,
    xDirectionUnknown = libmyo_x_direction_unknown
};

/// Firmware version of Myo.
struct FirmwareVersion {
    unsigned int firmwareVersionMajor; ///< Myo's major version must match the required major version.
    unsigned int firmwareVersionMinor; ///< Myo's minor version must match the required minor version.
    unsigned int firmwareVersionPatch; ///< Myo's patch version must greater or equal to the required patch version.
    unsigned int firmwareVersionHardwareRev; ///< Myo's hardware revision; not used to detect firmware version mismatch.
};

/// A DeviceListener receives events about a Myo.
/// @see Hub::addListener()
class DeviceListener {
public:
    virtual ~DeviceListener() {}

    /// Called when a Myo has been paired.
    /// @param myo The Myo for this event.
    /// @param timestamp The timestamp of the event. Timestamps are 64 bit unsigned integers that correspond to a number
    /// of microseconds since some (unspecified) period in time. Timestamps are monotonically non-decreasing.
    /// @param firmwareVersion The firmware version of \a myo.
    virtual void onPair(Myo* myo, uint64_t timestamp, FirmwareVersion firmwareVersion) {}

    /// Called when a Myo has been unpaired.
    /// @param myo The Myo for this event.
    /// @param timestamp The timestamp of the event. Timestamps are 64 bit unsigned integers that correspond to a number
    /// of microseconds since some (unspecified) period in time. Timestamps are monotonically non-decreasing.
    virtual void onUnpair(Myo* myo, uint64_t timestamp) {}

    /// Called when a paired Myo has been connected.
    /// @param myo The Myo for this event.
    /// @param timestamp The timestamp of the event. Timestamps are 64 bit unsigned integers that correspond to a number
    /// of microseconds since some (unspecified) period in time. Timestamps are monotonically non-decreasing.
    /// @param firmwareVersion The firmware version of \a myo.
    virtual void onConnect(Myo* myo, uint64_t timestamp, FirmwareVersion firmwareVersion) {}

    /// Called when a paired Myo has been disconnected.
    /// @param myo The Myo for this event.
    /// @param timestamp The timestamp of the event. Timestamps are 64 bit unsigned integers that correspond to a number
    /// of microseconds since some (unspecified) period in time. Timestamps are monotonically non-decreasing.
    virtual void onDisconnect(Myo* myo, uint64_t timestamp) {}

    /// Called when a paired Myo recognizes that it is on an arm.
    /// @param myo The Myo for this event.
    /// @param timestamp The timestamp of the event. Timestamps are 64 bit unsigned integers that correspond to a number
    /// of microseconds since some (unspecified) period in time. Timestamps are monotonically non-decreasing.
    /// @param arm The identified Arm of \a myo.
    /// @param xDirection The identified XDirection of \a myo.
    virtual void onArmSync(Myo* myo, uint64_t timestamp, Arm arm, XDirection xDirection) {}

    /// Called when a paired Myo is moved or removed from the arm.
    /// @param myo The Myo for this event.
    /// @param timestamp The timestamp of the event. Timestamps are 64 bit unsigned integers that correspond to a number
    /// of microseconds since some (unspecified) period in time. Timestamps are monotonically non-decreasing.
    virtual void onArmUnsync(Myo* myo, uint64_t timestamp) {}

    /// Called when a paired Myo becomes unlocked.
    /// @param myo The Myo for this event.
    /// @param timestamp The timestamp of the event. Timestamps are 64 bit unsigned integers that correspond to a number
    /// of microseconds since some (unspecified) period in time. Timestamps are monotonically non-decreasing.
    virtual void onUnlock(Myo* myo, uint64_t timestamp) {}

    /// Called when a paired Myo becomes locked.
    /// @param myo The Myo for this event.
    /// @param timestamp The timestamp of the event. Timestamps are 64 bit unsigned integers that correspond to a number
    /// of microseconds since some (unspecified) period in time. Timestamps are monotonically non-decreasing.
    virtual void onLock(Myo* myo, uint64_t timestamp) {}

    /// Called when a paired Myo has provided a new pose.
    /// @param myo The Myo for this event.
    /// @param timestamp The timestamp of the event. Timestamps are 64 bit unsigned integers that correspond to a number
    /// of microseconds since some (unspecified) period in time. Timestamps are monotonically non-decreasing.
    /// @param pose The identified Pose of \a myo.
    virtual void onPose(Myo* myo, uint64_t timestamp, Pose pose) {}

    /// Called when a paired Myo has provided new orientation data.
    /// @param myo The Myo for this event.
    /// @param timestamp The timestamp of the event. Timestamps are 64 bit unsigned integers that correspond to a number
    /// of microseconds since some (unspecified) period in time. Timestamps are monotonically non-decreasing.
    /// @param rotation The orientation data of \a myo, as a Quaternion.
    virtual void onOrientationData(Myo* myo, uint64_t timestamp, const Quaternion<float>& rotation) {}

    /// Called when a paired Myo has provided new accelerometer data in units of g.
    /// @param myo The Myo for this event.
    /// @param timestamp The timestamp of the event. Timestamps are 64 bit unsigned integers that correspond to a number
    /// of microseconds since some (unspecified) period in time. Timestamps are monotonically non-decreasing.
    /// @param accel The accelerometer data of \a myo, in units of g.
    virtual void onAccelerometerData(Myo* myo, uint64_t timestamp, const Vector3<float>& accel) {}

    /// Called when a paired Myo has provided new gyroscope data in units of deg/s.
    /// @param myo The Myo for this event.
    /// @param timestamp The timestamp of the event. Timestamps are 64 bit unsigned integers that correspond to a number
    /// of microseconds since some (unspecified) period in time. Timestamps are monotonically non-decreasing.
    /// @param gyro The gyroscope data of \a myo, in units of deg/s.
    virtual void onGyroscopeData(Myo* myo, uint64_t timestamp, const Vector3<float>& gyro) {}

    /// Called when a paired Myo has provided a new RSSI value.
    /// @param myo The Myo for this event.
    /// @param timestamp The timestamp of the event. Timestamps are 64 bit unsigned integers that correspond to a number
    /// of microseconds since some (unspecified) period in time. Timestamps are monotonically non-decreasing.
    /// @param rssi The RSSI (received signal strength indication) of \a myo.
    /// @see Myo::requestRssi() to request an RSSI value from the Myo.
    virtual void onRssi(Myo* myo, uint64_t timestamp, int8_t rssi) {}

    /// Called when a paired Myo has provided new EMG data.
    /// @param myo The Myo for this event.
    /// @param timestamp The timestamp of the event. Timestamps are 64 bit unsigned integers that correspond to a number
    /// of microseconds since some (unspecified) period in time. Timestamps are monotonically non-decreasing.
    /// @param emg An array of 8 elements, each corresponding to one sensor.
    virtual void onEmgData(myo::Myo* myo, uint64_t timestamp, const int8_t* emg) {}

    /// @cond LIBMYO_INTERNALS

    virtual void onOpaqueEvent(libmyo_event_t event) {}

    /// @endcond
};

} // namespace myo

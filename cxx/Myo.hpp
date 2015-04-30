// Copyright (C) 2013-2014 Thalmic Labs Inc.
// Distributed under the Myo SDK license agreement. See LICENSE.txt for details.
#pragma once

#include <myo/libmyo.h>

namespace myo {

/// Represents a Myo device with a specific MAC address.
/// This class can not be instantiated directly; instead, use Hub to get access to a Myo.
/// There is only one Myo instance corresponding to each device; thus, if the addresses of two Myo instances compare
/// equal, they refer to the same device.
class Myo {
public:
    /// Types of vibration supported by the Myo.
    enum VibrationType {
        vibrationShort  = libmyo_vibration_short,
        vibrationMedium = libmyo_vibration_medium,
        vibrationLong   = libmyo_vibration_long
    };

    /// Vibrate the Myo.
    void vibrate(VibrationType type);

    /// Request the RSSI of the Myo. An onRssi event will likely be generated with the value of the RSSI.
    /// @see DeviceListener::onRssi()
    void requestRssi() const;

    /// Unlock types supported by Myo.
    enum UnlockType {
        unlockTimed = libmyo_unlock_timed,
        unlockHold  = libmyo_unlock_hold
    };

    /// Unlock the Myo.
    /// Myo will remain unlocked for a short amount of time, after which it will automatically lock again.
    /// If Myo was locked, an onUnlock event will be generated.
    void unlock(UnlockType type);

    /// Force the Myo to lock immediately.
    /// If Myo was unlocked, an onLock event will be generated.
    void lock();

    /// Notify the Myo that a user action was recognized.
    /// Will cause Myo to vibrate.
    void notifyUserAction();

    /// Valid EMG streaming modes for a Myo.
    enum StreamEmgType {
        streamEmgDisabled = libmyo_stream_emg_disabled,
        streamEmgEnabled = libmyo_stream_emg_enabled
    };

    /// Sets the EMG streaming mode for a Myo.
    void setStreamEmg(StreamEmgType type);

    /// @cond MYO_INTERNALS

    /// Return the internal libmyo object corresponding to this device.
    libmyo_myo_t libmyoObject() const;

    /// @endcond

private:
    Myo(libmyo_myo_t myo);
    ~Myo();

    libmyo_myo_t _myo;

    // Not implemented.
    Myo(const Myo&);
    Myo& operator=(const Myo&);

    friend class Hub;
};

} // namespace myo

#include "impl/Myo_impl.hpp"

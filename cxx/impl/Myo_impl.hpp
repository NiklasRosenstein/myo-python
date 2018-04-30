// Copyright (C) 2013-2014 Thalmic Labs Inc.
// Distributed under the Myo SDK license agreement. See LICENSE.txt for details.
#include "../Myo.hpp"
#include "../detail/ThrowOnError.hpp"

#include <stdexcept>

namespace myo {

inline
void Myo::vibrate(VibrationType type)
{
    libmyo_vibrate(_myo, static_cast<libmyo_vibration_type_t>(type), ThrowOnError());
}

inline
void Myo::requestRssi() const
{
    libmyo_request_rssi(_myo, ThrowOnError());
}

inline
void Myo::requestBatteryLevel() const
{
    libmyo_request_battery_level(_myo, myo::ThrowOnError());
}

inline
void Myo::unlock(UnlockType type)
{
    libmyo_myo_unlock(_myo, static_cast<libmyo_unlock_type_t>(type), ThrowOnError());
}

inline
void Myo::lock()
{
    libmyo_myo_lock(_myo, ThrowOnError());
}

inline
void Myo::notifyUserAction()
{
    libmyo_myo_notify_user_action(_myo, libmyo_user_action_single, ThrowOnError());
}

inline
void Myo::setStreamEmg(StreamEmgType type)
{
    libmyo_set_stream_emg(_myo, static_cast<libmyo_stream_emg_t>(type), ThrowOnError());
}

inline
libmyo_myo_t Myo::libmyoObject() const
{
    return _myo;
}

inline
Myo::Myo(libmyo_myo_t myo)
: _myo(myo)
{
    if (!_myo) {
        throw std::invalid_argument("Cannot construct Myo instance with null pointer");
    }
}

inline
Myo::~Myo()
{
}

} // namespace myo

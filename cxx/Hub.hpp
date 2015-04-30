// Copyright (C) 2013-2014 Thalmic Labs Inc.
// Distributed under the Myo SDK license agreement. See LICENSE.txt for details.
#pragma once

#include <vector>

#include <myo/libmyo.h>

namespace myo {

class Myo;
class DeviceListener;

/// @brief A Hub provides access to one or more Myo instances.
class Hub {
public:
    /// Construct a hub.
    /// \a applicationIdentifier must follow a reverse domain name format (ex. com.domainname.appname). Application
    /// identifiers can be formed from the set of alphanumeric ASCII characters (a-z, A-Z, 0-9). The hyphen (-) and
    /// underscore (_) characters are permitted if they are not adjacent to a period (.) character  (i.e. not at the
    /// start or end of each segment), but are not permitted in the top-level domain. Application identifiers must have
    /// three or more segments. For example, if a company's domain is example.com and the application is named
    /// hello-world, one could use "com.example.hello-world" as a valid application identifier. \a applicationIdentifier
    /// can be an empty string.
    /// Throws an exception of type std::invalid_argument if \a applicationIdentifier is not in the proper reverse
    /// domain name format or is longer than 255 characters.
    /// Throws an exception of type std::runtime_error if the hub initialization failed for some reason, typically
    /// because Myo Connect is not running and a connection can thus not be established.
    Hub(const std::string& applicationIdentifier = "");

    /// Deallocate any resources associated with a Hub.
    /// This will cause all Myo instances retrieved from this Hub to become invalid.
    ~Hub();

    /// Wait for a Myo to become paired, or time out after \a timeout_ms milliseconds if provided.
    /// If \a timeout_ms is zero, this function blocks until a Myo is found.
    /// This function must not be called concurrently with run() or runOnce().
    Myo* waitForMyo(unsigned int milliseconds = 0);

    /// Register a listener to be called when device events occur.
    void addListener(DeviceListener* listener);

    /// Remove a previously registered listener.
    void removeListener(DeviceListener* listener);

    /// Locking policies supported by Myo.
    enum LockingPolicy {
        lockingPolicyNone     = libmyo_locking_policy_none,
        lockingPolicyStandard = libmyo_locking_policy_standard
    };

    /// Set the locking policy for Myos connected to the Hub.
    void setLockingPolicy(LockingPolicy lockingPolicy);

    /// Run the event loop for the specified duration (in milliseconds).
    void run(unsigned int duration_ms);

    /// Run the event loop until a single event occurs, or the specified duration (in milliseconds) has elapsed.
    void runOnce(unsigned int duration_ms);

    /// @cond MYO_INTERNALS

    /// Return the internal libmyo object corresponding to this hub.
    libmyo_hub_t libmyoObject();

protected:
    void onDeviceEvent(libmyo_event_t event);

    Myo* lookupMyo(libmyo_myo_t opaqueMyo) const;

    Myo* addMyo(libmyo_myo_t opaqueMyo);

    libmyo_hub_t _hub;
    std::vector<Myo*> _myos;
    std::vector<DeviceListener*> _listeners;

    /// @endcond

private:
    // Not implemented
    Hub(const Hub&);
    Hub& operator=(const Hub&);
};

/// @example hello-myo.cpp
/// @example multiple-myos.cpp
/// @example emg-data-sample.cpp

} // namespace myo

#include "impl/Hub_impl.hpp"

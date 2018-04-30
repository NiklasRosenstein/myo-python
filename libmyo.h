// Copyright (C) 2013-2014 Thalmic Labs Inc.
// Distributed under the Myo SDK license agreement. See LICENSE.txt for details.
#ifndef MYO_LIBMYO_H
#define MYO_LIBMYO_H

#include <stdint.h>

#include "libmyo/detail/visibility.h"

#ifdef __cplusplus
extern "C" {
#endif

/// @file libmyo.h
/// libmyo C API declarations.

typedef void* libmyo_hub_t;

/// \defgroup errors Error Handling
/// @{

/// Function result codes.
/// All libmyo functions that can fail return a value of this type.
typedef enum {
    libmyo_success,
    libmyo_error,
    libmyo_error_invalid_argument,
    libmyo_error_runtime
} libmyo_result_t;

/// Opaque handle to detailed error information.
typedef void* libmyo_error_details_t;

/// Return a null-terminated string with a detailed error message.
LIBMYO_EXPORT
const char* libmyo_error_cstring(libmyo_error_details_t);

/// Returns the kind of error that occurred.
LIBMYO_EXPORT
libmyo_result_t libmyo_error_kind(libmyo_error_details_t);

/// Free the resources allocated by an error object.
LIBMYO_EXPORT
void libmyo_free_error_details(libmyo_error_details_t);

/// @}

/// \defgroup libmyo_string Strings
/// @{

// Opaque string.
typedef void* libmyo_string_t;

// Return a null-terminated string from the opaque string.
LIBMYO_EXPORT
const char* libmyo_string_c_str(libmyo_string_t);

// Free the resources allocated by the string object.
LIBMYO_EXPORT
void libmyo_string_free(libmyo_string_t);

/// @}

/// \defgroup libmyo_direct_mac_addresses MAC address utilities
/// @{

/// Retrieve the string representation of a MAC address in hex.
/// Returns a string in the format of 00-00-00-00-00-00.
LIBMYO_EXPORT
libmyo_string_t libmyo_mac_address_to_string(uint64_t);

/// Retrieve the MAC address from a null-terminated string in the format of 00-00-00-00-00-00.
/// Returns 0 if the string does not match the format.
LIBMYO_EXPORT
uint64_t libmyo_string_to_mac_address(const char*);

/// @}

/// @defgroup libmyo_hub Hub instance
/// @{

/// Initialize a connection to the hub.
/// \a application_identifier must follow a reverse domain name format (ex. com.domainname.appname). Application
/// identifiers can be formed from the set of alphanumeric ASCII characters (a-z, A-Z, 0-9). The hyphen (-) and
/// underscore (_) characters are permitted if they are not adjacent to a period (.) character (i.e. not at the start or
/// end of each segment), but are not permitted in the top-level domain. Application identifiers must have three or more
/// segments. For example, if a company's domain is example.com and the application is named hello-world, one could use
/// "com.example.hello-world" as a valid application identifier. \a application_identifier can be NULL or empty.
/// @returns libmyo_success if the connection is successfully established, otherwise:
///  - libmyo_error_runtime if a connection could not be established
///  - libmyo_error_invalid_argument if \a out_hub is NULL
///  - libmyo_error_invalid_argument if \a application_identifier is longer than 255 characters
///  - libmyo_error_invalid_argument if \a application_identifier is not in the proper reverse domain name format
LIBMYO_EXPORT
libmyo_result_t libmyo_init_hub(libmyo_hub_t* out_hub, const char* application_identifier,
                                libmyo_error_details_t* out_error);

/// Free the resources allocated to a hub.
/// @returns libmyo_success if shutdown is successful, otherwise:
///  - libmyo_error_invalid_argument if \a hub is NULL
///  - libmyo_error if \a hub is not a valid hub
LIBMYO_EXPORT
libmyo_result_t libmyo_shutdown_hub(libmyo_hub_t hub, libmyo_error_details_t* out_error);

// Locking policies.
typedef enum {
    libmyo_locking_policy_none,    ///< Pose events are always sent.
    libmyo_locking_policy_standard ///< Pose events are not sent while a Myo is locked.
} libmyo_locking_policy_t;

/// Set the locking policy for Myos connected to the hub.
/// @returns libmyo_success if the locking policy is successfully set, otherwise
///  - libmyo_error_invalid_argument if \a hub is NULL
///  - libmyo_error if \a hub is not a valid hub
LIBMYO_EXPORT
libmyo_result_t libmyo_set_locking_policy(libmyo_hub_t hub, libmyo_locking_policy_t locking_policy,
                                          libmyo_error_details_t* out_error);

/// @}

/// @defgroup libmyo_myo Myo instances
/// @{

/// Opaque type corresponding to a known Myo device.
typedef void* libmyo_myo_t;

/// Types of vibration
typedef enum {
    libmyo_vibration_short,
    libmyo_vibration_medium,
    libmyo_vibration_long
} libmyo_vibration_type_t;

/// Retrieve the MAC address of a Myo.
/// The MAC address is unique to the physical Myo, and is a 48-bit number.
LIBMYO_EXPORT
uint64_t libmyo_get_mac_address(libmyo_myo_t myo);

/// Vibrate the given myo.
/// Can be called when a Myo is paired.
/// @returns libmyo_success if the Myo successfully vibrated, otherwise
///  - libmyo_error_invalid_argument if \a myo is NULL
LIBMYO_EXPORT
libmyo_result_t libmyo_vibrate(libmyo_myo_t myo, libmyo_vibration_type_t type, libmyo_error_details_t* out_error);

/// Request the RSSI for a given myo.
/// Can be called when a Myo is paired. A libmyo_event_rssi event will likely be generated with the value of the RSSI.
/// @returns libmyo_success if the Myo successfully got the RSSI, otherwise
///  - libmyo_error_invalid_argument if \a myo is NULL
LIBMYO_EXPORT
libmyo_result_t libmyo_request_rssi(libmyo_myo_t myo, libmyo_error_details_t* out_error);


/// Request the battery level for a given Myo.
/// A libmyo_event_battery_level event will be generated with the value of the battery level.
/// @returns libmyo_success if the Myo successfully requested the battery level, otherwise
///  - libmyo_error_invalid_argument if \a myo is NULL
LIBMYO_EXPORT
libmyo_result_t libmyo_request_battery_level(libmyo_myo_t myo_opq, libmyo_error_details_t* out_error);

/// EMG streaming modes.
typedef enum {
    libmyo_stream_emg_disabled, ///< Do not send EMG data.
    libmyo_stream_emg_enabled   ///< Send EMG data.
} libmyo_stream_emg_t;

/// Set whether or not to stream EMG data for a given myo.
/// Can be called when a Myo is paired.
/// @returns libmyo_success if the EMG mode was set successfully, otherwise
///  - libmyo_error_invalid_argument if \a myo is NULL
LIBMYO_EXPORT
libmyo_result_t libmyo_set_stream_emg(libmyo_myo_t myo, libmyo_stream_emg_t emg, libmyo_error_details_t* out_error);

/// @}

/// @defgroup libmyo_poses Pose recognition.
/// @{

/// Supported poses.
typedef enum {
    libmyo_pose_rest           = 0, ///< Rest pose.
    libmyo_pose_fist           = 1, ///< User is making a fist.
    libmyo_pose_wave_in        = 2, ///< User has an open palm rotated towards the posterior of their wrist.
    libmyo_pose_wave_out       = 3, ///< User has an open palm rotated towards the anterior of their wrist.
    libmyo_pose_fingers_spread = 4, ///< User has an open palm with their fingers spread away from each other.
    libmyo_pose_double_tap     = 5, ///< User tapped their thumb and middle finger together twice in succession.

    libmyo_num_poses,               ///< Number of poses supported; not a valid pose.

    libmyo_pose_unknown = 0xffff    ///< Unknown pose.
} libmyo_pose_t;

/// @}

/// @defgroup libmyo_locking Myo locking mechanism

/// Valid unlock types.
typedef enum {
    libmyo_unlock_timed = 0, ///< Unlock for a fixed period of time.
    libmyo_unlock_hold  = 1, ///< Unlock until explicitly told to re-lock.
} libmyo_unlock_type_t;

/// Unlock the given Myo.
/// Can be called when a Myo is paired. A libmyo_event_unlocked event will be generated if the Myo was locked.
/// @returns libmyo_success if the Myo was successfully unlocked, otherwise
///  - libmyo_error_invalid_argument if \a myo is NULL
LIBMYO_EXPORT
libmyo_result_t libmyo_myo_unlock(libmyo_myo_t myo, libmyo_unlock_type_t type, libmyo_error_details_t* out_error);

/// Lock the given Myo immediately.
/// Can be called when a Myo is paired. A libmyo_event_locked event will be generated if the Myo was unlocked.
/// @returns libmyo_success if the Myo was successfully locked, otherwise
///  - libmyo_error_invalid_argument if \a myo is NULL
LIBMYO_EXPORT
libmyo_result_t libmyo_myo_lock(libmyo_myo_t myo, libmyo_error_details_t* out_error);

/// User action types.
typedef enum {
    libmyo_user_action_single = 0, ///< User did a single, discrete action, such as pausing a video.
} libmyo_user_action_type_t;

/// Notify the given Myo that a user action was recognized.
/// Can be called when a Myo is paired. Will cause Myo to vibrate.
/// @returns libmyo_success if the Myo was successfully notified, otherwise
///  - libmyo_error_invalid_argument if \a myo is NULL
LIBMYO_EXPORT
libmyo_result_t libmyo_myo_notify_user_action(libmyo_myo_t myo, libmyo_user_action_type_t type,
                                              libmyo_error_details_t* out_error);

/// @}

/// @defgroup libmyo_events Event Handling
/// @{

/// Types of events.
typedef enum {
    libmyo_event_paired,           ///< Successfully paired with a Myo.
    libmyo_event_unpaired,         ///< Successfully unpaired from a Myo.
    libmyo_event_connected,        ///< A Myo has successfully connected.
    libmyo_event_disconnected,     ///< A Myo has been disconnected.
    libmyo_event_arm_synced,       ///< A Myo has recognized that the sync gesture has been successfully performed.
    libmyo_event_arm_unsynced,     ///< A Myo has been moved or removed from the arm.
    libmyo_event_orientation,      ///< Orientation data has been received.
    libmyo_event_pose,             ///< A change in pose has been detected. @see libmyo_pose_t.
    libmyo_event_rssi,             ///< An RSSI value has been received.
    libmyo_event_unlocked,         ///< A Myo has become unlocked.
    libmyo_event_locked,           ///< A Myo has become locked.
    libmyo_event_emg,              ///< EMG data has been received.
    libmyo_event_battery_level,    ///< A battery level value has been received.
    libmyo_event_warmup_completed, ///< The warmup period has completed.
} libmyo_event_type_t;

/// Information about an event.
typedef const void* libmyo_event_t;

/// Retrieve the type of an event.
LIBMYO_EXPORT
uint32_t libmyo_event_get_type(libmyo_event_t event);

/// Retrieve the timestamp of an event.
/// @see libmyo_now() for details on timestamps.
LIBMYO_EXPORT
uint64_t libmyo_event_get_timestamp(libmyo_event_t event);

/// Retrieve the Myo associated with an event.
LIBMYO_EXPORT
libmyo_myo_t libmyo_event_get_myo(libmyo_event_t event);

/// Retrieve the MAC address of the myo associated with an event.
LIBMYO_EXPORT
uint64_t libmyo_event_get_mac_address(libmyo_event_t event_opq);

/// Retrieve the name of the myo associated with an event.
/// Caller must free the returned string. @see libmyo_string functions.
LIBMYO_EXPORT
libmyo_string_t libmyo_event_get_myo_name(libmyo_event_t event);

/// Components of version.
typedef enum {
    libmyo_version_major,        ///< Major version.
    libmyo_version_minor,        ///< Minor version.
    libmyo_version_patch,        ///< Patch version.
    libmyo_version_hardware_rev, ///< Hardware revision.
} libmyo_version_component_t;

/// Hardware revisions.
typedef enum {
    libmyo_hardware_rev_c = 1, ///< Alpha units
    libmyo_hardware_rev_d = 2, ///< Consumer units
} libmyo_hardware_rev_t;

/// Retrieve the Myo armband's firmware version from this event.
/// Valid for libmyo_event_paired and libmyo_event_connected events.
LIBMYO_EXPORT
unsigned int libmyo_event_get_firmware_version(libmyo_event_t event, libmyo_version_component_t);

/// Enumeration identifying a right arm or left arm. @see libmyo_event_get_arm().
typedef enum {
    libmyo_arm_right, ///< Myo is on the right arm.
    libmyo_arm_left, ///< Myo is on the left arm.
    libmyo_arm_unknown, ///< Unknown arm.
} libmyo_arm_t;

/// Retrieve the arm associated with an event.
/// Valid for libmyo_event_arm_synced events only.
LIBMYO_EXPORT
libmyo_arm_t libmyo_event_get_arm(libmyo_event_t event);

/// Possible directions for Myo's +x axis relative to a user's arm.
typedef enum {
    libmyo_x_direction_toward_wrist, ///< Myo's +x axis is pointing toward the user's wrist.
    libmyo_x_direction_toward_elbow, ///< Myo's +x axis is pointing toward the user's elbow.
    libmyo_x_direction_unknown, ///< Unknown +x axis direction.
} libmyo_x_direction_t;

/// Retrieve the x-direction associated with an event.
/// The x-direction specifies which way Myo's +x axis is pointing relative to the user's arm.
/// Valid for libmyo_event_arm_synced events only.
LIBMYO_EXPORT
libmyo_x_direction_t libmyo_event_get_x_direction(libmyo_event_t event);

/// Possible warmup states for Myo.
typedef enum {
    libmyo_warmup_state_unknown = 0, ///< Unknown warm up state.
    libmyo_warmup_state_cold    = 1, ///< Myo needs to warm up.
    libmyo_warmup_state_warm    = 2, ///< Myo is already in a warmed up state.
} libmyo_warmup_state_t;

/// Retrieve the warmup state of the Myo associated with an event.
/// Valid for libmyo_event_arm_synced events only.
LIBMYO_EXPORT
libmyo_warmup_state_t libmyo_event_get_warmup_state(libmyo_event_t event);

/// Possible warmup results for Myo.
typedef enum {
    libmyo_warmup_result_unknown        = 0, ///< Unknown warm up result.
    libmyo_warmup_result_success        = 1, ///< The warm up period has completed successfully.
    libmyo_warmup_result_failed_timeout = 2, ///< The warm up period timed out.
} libmyo_warmup_result_t;

/// Retrieve the warmup result of the Myo associated with an event.
/// Valid for libmyo_event_warmup_completed events only.
LIBMYO_EXPORT
libmyo_warmup_result_t libmyo_event_get_warmup_result(libmyo_event_t event);

/// Retrieve the estimated rotation of Myo on the user's arm after a sync.
/// The values specifies the rotation of the myo on the arm (0 - logo facing down, pi - logo facing up)
/// Only supported by FW 1.3.x and above (older firmware will always report 0 for the rotation)
/// Valid for libmyo_event_arm_synced events only.
LIBMYO_EXPORT
float libmyo_event_get_rotation_on_arm(libmyo_event_t event);

/// Index into orientation data, which is provided as a quaternion.
/// Orientation data is returned as a unit quaternion of floats, represented as `w + x * i + y * j + z * k`.
typedef enum {
    libmyo_orientation_x = 0, ///< First component of the quaternion's vector part
    libmyo_orientation_y = 1, ///< Second component of the quaternion's vector part
    libmyo_orientation_z = 2, ///< Third component of the quaternion's vector part
    libmyo_orientation_w = 3, ///< Scalar component of the quaternion.
} libmyo_orientation_index;

/// Retrieve orientation data associated with an event.
/// Valid for libmyo_event_orientation events only.
/// @see libmyo_orientation_index
LIBMYO_EXPORT
float libmyo_event_get_orientation(libmyo_event_t event, libmyo_orientation_index index);

/// Retrieve raw accelerometer data associated with an event in units of g.
/// Valid for libmyo_event_orientation events only.
/// Requires `index < 3`.
LIBMYO_EXPORT
float libmyo_event_get_accelerometer(libmyo_event_t event, unsigned int index);

/// Retrieve raw gyroscope data associated with an event in units of deg/s.
/// Valid for libmyo_event_orientation events only.
/// Requires `index < 3`.
LIBMYO_EXPORT
float libmyo_event_get_gyroscope(libmyo_event_t event, unsigned int index);

/// Retrieve the pose associated with an event.
/// Valid for libmyo_event_pose events only.
LIBMYO_EXPORT
libmyo_pose_t libmyo_event_get_pose(libmyo_event_t event);

/// Retreive the RSSI associated with an event.
/// Valid for libmyo_event_rssi events only.
LIBMYO_EXPORT
int8_t libmyo_event_get_rssi(libmyo_event_t event);

/// Retrieve the battery level of the Myo armband associated with an event.
/// Only valid for libmyo_event_battery_level event.
LIBMYO_EXPORT
uint8_t libmyo_event_get_battery_level(libmyo_event_t event);

/// Retrieve an EMG data point associated with an event.
/// Valid for libmyo_event_emg events only.
/// @a sensor must be smaller than 8.
LIBMYO_EXPORT
int8_t libmyo_event_get_emg(libmyo_event_t event, unsigned int sensor);

/// Return type for event handlers.
typedef enum {
    libmyo_handler_continue, ///< Continue processing events
    libmyo_handler_stop,     ///< Stop processing events
} libmyo_handler_result_t;

/// Callback function type to handle events as they occur from libmyo_run().
typedef libmyo_handler_result_t (*libmyo_handler_t)(void* user_data, libmyo_event_t event);

/// Process events and call the provided callback as they occur.
/// Runs for up to approximately \a duration_ms milliseconds or until a called handler returns libmyo_handler_stop.
/// @returns libmyo_success after a successful run, otherwise
///  - libmyo_error_invalid_argument if \a hub is NULL
///  - libmyo_error_invalid_argument if \a handler is NULL
LIBMYO_EXPORT
libmyo_result_t libmyo_run(libmyo_hub_t hub, unsigned int duration_ms, libmyo_handler_t handler, void* user_data,
                           libmyo_error_details_t* out_error);

/// @}

#ifdef __cplusplus
} // extern "C"
#endif

#endif // MYO_LIBMYO_H

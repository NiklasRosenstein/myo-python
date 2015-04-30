// Copyright (C) 2013-2014 Thalmic Labs Inc.
// Distributed under the Myo SDK license agreement. See LICENSE.txt for details.
#ifndef MYO_LIBMYO_DETAIL_VISIBILITY_H
#define MYO_LIBMYO_DETAIL_VISIBILITY_H

#if defined(_WIN32) || defined(__CYGWIN__)
  #ifdef myo_EXPORTS
    #ifdef __GNUC__
      #define LIBMYO_EXPORT __attribute__ ((dllexport))
    #else
      #define LIBMYO_EXPORT __declspec(dllexport)
    #endif
  #else
    #ifdef LIBMYO_STATIC_BUILD
      #define LIBMYO_EXPORT
    #else
      #ifdef __GNUC__
        #define LIBMYO_EXPORT __attribute__ ((dllimport))
      #else
        #define LIBMYO_EXPORT __declspec(dllimport)
      #endif
    #endif
  #endif
#else
  #if __GNUC__ >= 4
    #define LIBMYO_EXPORT __attribute__ ((visibility ("default")))
  #else
    #define LIBMYO_EXPORT
  #endif
#endif

#endif // MYO_LIBMYO_DETAIL_VISIBILITY_H

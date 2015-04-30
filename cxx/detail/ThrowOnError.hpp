// Copyright (C) 2013-2014 Thalmic Labs Inc.
// Distributed under the Myo SDK license agreement. See LICENSE.txt for details.
#ifndef MYO_CXX_DETAIL_THROWONERROR_HPP
#define MYO_CXX_DETAIL_THROWONERROR_HPP

#include <stdexcept>

#include <myo/libmyo.h>

#if defined(_MSC_VER) && _MSC_VER <= 1800
#define LIBMYO_NOEXCEPT(b)
#else
#if __cplusplus >= 201103L
# define LIBMYO_NOEXCEPT(b) noexcept(b)
#else
# define LIBMYO_NOEXCEPT(b)
#endif
#endif

namespace myo {

class ThrowOnError {
public:
    ThrowOnError()
    : _error()
    {
    }

    ~ThrowOnError() LIBMYO_NOEXCEPT(false)
    {
        if (_error)
        {
            switch (libmyo_error_kind(_error)) {
            case libmyo_error:
            case libmyo_error_runtime:
            {
                std::runtime_error exception(libmyo_error_cstring(_error));
                libmyo_free_error_details(_error);
                throw exception;
            }
            case libmyo_error_invalid_argument:
            {
                std::invalid_argument exception(libmyo_error_cstring(_error));
                libmyo_free_error_details(_error);
                throw exception;
            }
            case libmyo_success:
            {
                break;
            }
            }
        }
    }

    operator libmyo_error_details_t*()
    {
        return &_error;
    }

private:
    libmyo_error_details_t _error;

    // Not implemented
    ThrowOnError(const ThrowOnError&); // = delete;
    ThrowOnError& operator=(const ThrowOnError&); // = delete;
};

} //namespace libmyo

#endif // MYO_CXX_DETAIL_THROWONERROR_HPP

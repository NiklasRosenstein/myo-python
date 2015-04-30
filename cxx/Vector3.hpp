// Copyright (C) 2013-2014 Thalmic Labs Inc.
// Distributed under the Myo SDK license agreement. See LICENSE.txt for details.
#pragma once

#define _USE_MATH_DEFINES
#include <cmath>

namespace myo {

/// A vector of three components.
/// This type provides very basic functionality to store a three dimensional vector that's sufficient to retrieve
/// the data to be placed in a full featured vector type. A few common vector operations, such as dot product and
/// cross product, are also provided.
template<typename T>
class Vector3 {
  public:
    /// Construct a vector of all zeroes.
    Vector3()
    {
        _data[0] = 0;
        _data[1] = 0;
        _data[2] = 0;
    }

    /// Construct a vector with the three provided components.
    Vector3(T x, T y, T z)
    {
        _data[0] = x;
        _data[1] = y;
        _data[2] = z;
    }

    /// Construct a vector with the same components as \a other.
    Vector3(const Vector3& other)
    {
        *this = other;
    }

    /// Set the components of this vector to be the same as \a other.
    Vector3& operator=(const Vector3& other)
    {
        _data[0] = other._data[0];
        _data[1] = other._data[1];
        _data[2] = other._data[2];

        return *this;
    }

    /// Return a copy of the component of this vector at \a index, which should be 0, 1, or 2.
    T operator[](unsigned int index) const
    {
        return _data[index];
    }

    /// Return the x-component of this vector.
    T x() const { return _data[0]; }

    /// Return the y-component of this vector.
    T y() const { return _data[1]; }

    /// Return the z-component of this vector.
    T z() const { return _data[2]; }

    /// Return the magnitude of this vector.
    T magnitude() const
    {
        return std::sqrt(x() * x() + y() * y() + z() * z());
    }

    /// Return a normalized copy of this vector.
    Vector3 normalized() const
    {
        T norm = magnitude();
        return Vector3(x() / norm, y() / norm, z() / norm);
    }

    /// Return the dot product of this vector and \a rhs.
    T dot(const Vector3& rhs) const
    {
        return x() * rhs.x() + y() * rhs.y() + z() * rhs.z();
    }

    /// Return the cross product of this vector and \a rhs.
    Vector3 cross(const Vector3& rhs) const
    {
        return Vector3(
            y() * rhs.z() - z() * rhs.y(),
            z() * rhs.x() - x() * rhs.z(),
            x() * rhs.y() - y() * rhs.x()
        );
    }

    /// Return the angle between this vector and \a rhs, in radians.
    T angleTo(const Vector3& rhs) const
    {
        return std::acos(dot(rhs) / (magnitude() * rhs.magnitude()));
    }

  private:
    T _data[3];
};

} // namespace myo

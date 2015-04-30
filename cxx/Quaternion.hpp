// Copyright (C) 2013-2014 Thalmic Labs Inc.
// Distributed under the Myo SDK license agreement. See LICENSE.txt for details.
#pragma once

#include <cmath>

#include "Vector3.hpp"

namespace myo {

/// A quaternion that can be used to represent a rotation.
/// This type provides only very basic functionality to store quaternions that's sufficient to retrieve the data to
/// be placed in a full featured quaternion type.
template<typename T>
class Quaternion {
  public:
    /// Construct a quaternion that represents zero rotation (i.e. the multiplicative identity).
    Quaternion()
    : _x(0)
    , _y(0)
    , _z(0)
    , _w(1)
    {
    }

    /// Construct a quaternion with the provided components.
    Quaternion(T x, T y, T z, T w)
    : _x(x)
    , _y(y)
    , _z(z)
    , _w(w)
    {
    }

    /// Set the components of this quaternion to be those of the other.
    Quaternion& operator=(const Quaternion other)
    {
        _x = other._x;
        _y = other._y;
        _z = other._z;
        _w = other._w;

        return *this;
    }

    /// Return the x-component of this quaternion's vector.
    T x() const { return _x; }

    /// Return the y-component of this quaternion's vector.
    T y() const { return _y; }

    /// Return the z-component of this quaternion's vector.
    T z() const { return _z; }

    /// Return the w-component (scalar) of this quaternion.
    T w() const { return _w; }

    /// Return the quaternion multiplied by \a rhs.
    /// Note that quaternion multiplication is not commutative.
    Quaternion operator*(const Quaternion& rhs) const
    {
        return Quaternion(
            _w * rhs._x + _x * rhs._w + _y * rhs._z - _z * rhs._y,
            _w * rhs._y - _x * rhs._z + _y * rhs._w + _z * rhs._x,
            _w * rhs._z + _x * rhs._y - _y * rhs._x + _z * rhs._w,
            _w * rhs._w - _x * rhs._x - _y * rhs._y - _z * rhs._z
        );
    }

    /// Multiply this quaternion by \a rhs.
    /// Return this quaternion updated with the result.
    Quaternion& operator*=(const Quaternion& rhs)
    {
        *this = *this * rhs;
        return *this;
    }

    /// Return the unit quaternion corresponding to the same rotation as this one.
    Quaternion normalized() const
    {
        T magnitude = std::sqrt(_x * _x + _y * _y + _z * _z + _w * _w);

        return Quaternion(_x / magnitude, _y / magnitude, _z / magnitude, _w / magnitude);
    }

    /// Return this quaternion's conjugate.
    Quaternion conjugate() const
    {
        return Quaternion(-_x, -_y, -_z, _w);
    }

    /// Return a quaternion that represents a right-handed rotation of \a angle radians about the given \a axis.
    /// \a axis The unit vector representing the axis of rotation.
    /// \a angle The angle of rotation, in radians.
    static Quaternion fromAxisAngle(const myo::Vector3<T>& axis, T angle)
    {
        return Quaternion(axis.x() * std::sin(angle / 2),
                          axis.y() * std::sin(angle / 2),
                          axis.z() * std::sin(angle / 2),
                          std::cos(angle / 2));
    }

  private:
    T _x, _y, _z, _w;
};

/// Return a copy of this \a vec rotated by \a quat.
/// \relates myo::Quaternion
template<typename T>
Vector3<T> rotate(const Quaternion<T>& quat, const Vector3<T>& vec)
{
    myo::Quaternion<T> qvec(vec.x(), vec.y(), vec.z(), 0);
    myo::Quaternion<T> result = quat * qvec * quat.conjugate();
    return Vector3<T>(result.x(), result.y(), result.z());
}

/// Return a quaternion that represents a rotation from vector \a from to \a to.
/// \relates myo::Quaternion
/// See http://stackoverflow.com/questions/1171849/finding-quaternion-representing-the-rotation-from-one-vector-to-another
/// for some explanation.
template<typename T>
Quaternion<T> rotate(const Vector3<T>& from, const Vector3<T>& to)
{
    Vector3<T> cross = from.cross(to);

    // The product of the square of magnitudes and the cosine of the angle between from and to.
    T cosTheta = from.dot(to);

    // Return identity if the vectors are the same direction.
    if (cosTheta >= 1) {
        return Quaternion<T>();
    }

    // The product of the square of the magnitudes
    T k = std::sqrt(from.dot(from) * to.dot(to));

    // Return identity in the degenerate case.
    if (k <= 0) {
        return Quaternion<T>();
    }

    // Special handling for vectors facing opposite directions.
    if (cosTheta / k <= -1) {
        Vector3<T> xAxis(1, 0, 0);
        Vector3<T> yAxis(0, 1, 0);

        cross = from.cross(std::abs(from.dot(xAxis)) < 1 ? xAxis : yAxis);
        k = cosTheta = 0;
    }

    return Quaternion<T>(
        cross.x(),
        cross.y(),
        cross.z(),
        k + cosTheta);
}

} // namespace myo

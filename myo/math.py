# The MIT License (MIT)
#
# Copyright (c) 2015-2018 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import math
import six


class Vector(object):
  """
  A three-dimensional vector.
  """

  __slots__ = ('x', 'y', 'z')

  def __init__(self, x, y, z):
    super(Vector, self).__init__()
    self.x = float(x)
    self.y = float(y)
    self.z = float(z)

  def __mul__(self, rhs):
    """
    Multiplies the vector with *rhs* which can be either a scalar
    to retrieve a new Vector or another vector to compute the dot
    product.
    """

    if isinstance(rhs, (six.integer_types, float)):
      return Vector(self.x * rhs, self.y * rhs, self.z * rhs)
    else:
      return self.dot(rhs)

  def __add__(self, rhs):
    """
    Adds *self* to *rhs* and returns a new vector.
    """

    if isinstance(rhs, (six.integer_types, float)):
      return Vector(self.x + rhs, self.y + rhs, self.z + rhs)
    else:
      return Vector(self.x + rhs.x, self.y + rhs.y, self.z + rhs.z)

  def __sub__(self, rhs):
    """
    Substracts *self* from *rhs* and returns a new vector.
    """

    if isinstance(rhs, (six.integer_types, float)):
      return Vector(self.x - rhs, self.y - rhs, self.z - rhs)
    else:
      return Vector(self.x - rhs.x, self.y - rhs.y, self.z - rhs.z)

  def __iter__(self):
    return iter((self.x, self.y, self.z))

  def __repr__(self):
    return 'Vector({0}, {1}, {2})'.format(self.x, self.y, self.z)

  def __invert__(self):
    """
    Returns the inversion of the vector.
    """

    return Vector(-self.x, -self.y, -self.z)

  def __getitem__(self, index):
    return (self.x, self.y, self.z)[index]

  def copy(self):
    """
    Returns a shallow copy of the vector.
    """

    return Vector(self.x, self.y, self.z)

  def magnitude(self):
    """
    Return the magnitude of this vector.
    """

    return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

  def normalized(self):
    """
    Returns a normalized copy of this vector.
    """

    norm = self.magnitude()
    return Vector(self.x / norm, self.y / norm, self.z / norm)

  def dot(self, rhs):
    """
    Return the dot product of this vector and *rhs*.
    """

    return self.x * rhs.x + self.y * rhs.y + self.z * rhs.z

  def cross(self, rhs):
    """
    Return the cross product of this vector and *rhs*.
    """

    return Vector(
      self.y * rhs.z - self.z * rhs.y,
      self.z * rhs.x - self.x * rhs.z,
      self.x * rhs.y - self.y * rhs.x)

  def angle_to(self, rhs):
    """
    Return the angle between this vector and *rhs* in radians.
    """

    return math.acos(self.dot(rhs) / (self.magnitude() * rhs.magnitude()))

  __abs__ = magnitude


class Quaternion(object):
  """
  This class represents a quaternion which can be used to represent
  gimbal-lock free rotations.

  This implementation can work with any vector type that has members
  x, y and z and it has a constructor that accepts values for these
  members in order. This is convenient when combining the Myo SDK
  with other 3D APIs that provide a vector class.
  """

  __slots__ = ('x', 'y', 'z', 'w')

  def __init__(self, x, y, z, w):
    super(Quaternion, self).__init__()
    self.x = float(x)
    self.y = float(y)
    self.z = float(z)
    self.w = float(w)

  def __mul__(self, rhs):
    """
    Multiplies *self* with the #Quaternion *rhs* and returns a new #Quaternion.
    """

    if not isinstance(rhs, Quaternion):
      raise TypeError('can only multiply with Quaternion')
    return Quaternion(
      self.w * rhs.x + self.x * rhs.w + self.y * rhs.z - self.z * rhs.y,
      self.w * rhs.y - self.x * rhs.z + self.y * rhs.w + self.z * rhs.x,
      self.w * rhs.z + self.x * rhs.y - self.y * rhs.x + self.z * rhs.w,
      self.w * rhs.w - self.x * rhs.x - self.y * rhs.y - self.z * rhs.z)

  def __iter__(self):
    return iter((self.x, self.y, self.z, self.w))

  def __repr__(self):
    return '{0}({1}, {2}, {3}, {4})'.format(
      type(self).__name__, self.x, self.y, self.z, self.w)

  def __invert__(self):
    """
    Returns this Quaternion's conjugate.
    """

    return Quaternion(-self.x, -self.y, -self.z, self.w)

  def __getitem__(self, index):
    return (self.x, self.y, self.z, self.w)[index]

  def copy(self):
    """
    Returns a shallow copy of the quaternion.
    """

    return Quaternion(self.x, self.y, self.z, self.w)

  def magnitude(self):
    """
    Returns the magnitude of the quaternion.
    """

    return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2 + self.w ** 2)

  def normalized(self):
    """
    Returns the unit quaternion corresponding to the same rotation
    as this one.
    """

    magnitude = self.magnitude()
    return Quaternion(
      self.x / magnitude, self.y / magnitude,
      self.z / magnitude, self.w / magnitude)

  conjugate = __invert__

  def rotate(self, vec):
    """
    Returns *vec* rotated by this #Quaternion.

    :param vec: A vector object.
    :return: object of type of *vec*
    """

    qvec = self * Quaternion(vec.x, vec.y, vec.z, 0) * ~self
    return type(vec)(qvec.x, qvec.y, qvec.z)

  # Reference:
  # http://answers.unity3d.com/questions/416169/finding-pitchrollyaw-from-quaternions.html

  @property
  def roll(self):
    """ Calculates the Roll of the Quaternion. """

    x, y, z, w = self.x, self.y, self.z, self.w
    return math.atan2(2*y*w - 2*x*z, 1 - 2*y*y - 2*z*z)

  @property
  def pitch(self):
    """ Calculates the Pitch of the Quaternion. """

    x, y, z, w = self.x, self.y, self.z, self.w
    return math.atan2(2*x*w - 2*y*z, 1 - 2*x*x - 2*z*z)

  @property
  def yaw(self):
    """ Calculates the Yaw of the Quaternion. """

    x, y, z, w = self.x, self.y, self.z, self.w
    return math.asin(2*x*y + 2*z*w)

  @property
  def rpy(self):
    """ Calculates the Roll, Pitch and Yaw of the Quaternion. """

    x, y, z, w = self.x, self.y, self.z, self.w
    roll = math.atan2(2*y*w - 2*x*z, 1 - 2*y*y - 2*z*z)
    pitch = math.atan2(2*x*w - 2*y*z, 1 - 2*x*x - 2*z*z)
    yaw = math.asin(2*x*y + 2*z*w)
    return (roll, pitch, yaw)

  @staticmethod
  def identity():
    """
    Returns the identity #Quaternion.
    """

    return Quaternion(0, 0, 0, 1)

  @staticmethod
  def rotation_of(source, dest):
    """
    Returns a #Quaternion that represents a rotation from vector
    *source* to *dest*.
    """

    source = Vector(source.x, source.y, source.z)
    dest = Vector(dest.x, dest.y, dest.z)
    cross = source.cross(dest)
    cos_theta = source.dot(dest)

    # Return identity if the vectors are the same direction.
    if cos_theta >= 1.0:
      return Quaternion.identity()

    # Product of the square of the magnitudes.
    k = math.sqrt(source.dot(source), dest.dot(dest))

    # Return identity in the degenerate case.
    if k <= 0.0:
      return Quaternion.identity()

    # Special handling for vectors facing opposite directions.
    if cos_theta / k <= -1:
      x_axis = Vector(1, 0, 0)
      y_axis = Vector(0, 1, 1)
      if abs(source.dot(x_ais)) < 1.0:
        cross = source.cross(x_axis)
      else:
        cross = source.cross(y_axis)

    return Quaternion(cross.x, cross.y, cross.z, k + cos_theta)

  @staticmethod
  def from_axis_angle(axis, angle):
    """
    Returns a #Quaternion that represents the right-handed
    rotation of *angle* radians about the givne *axis*.

    :param axis: The unit vector representing the axis of rotation.
    :param angle: The angle of rotation, in radians.
    """

    sincomp = math.sin(angle / 2.0)
    return Quaternion(
      axis.x * sincomp, axis.y * sincomp,
      axis.z * sincomp, math.cos(angle / 2.0))

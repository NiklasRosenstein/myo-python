# Copyright (c) 2015  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
Provides a 3 dimensional vector class.
"""

import math
import six


class Vector(object):

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

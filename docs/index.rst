
``myo-python`` - Python bindings for the Myo SDK
================================================

.. toctree::
  :caption: Table of Contents

  myo
  myo.utils
  myo.lowlevel


Introduction

This module is a :mod:`ctypes` based wrapper for the Thalmic Myo SDK that
is compatible with Python 2 and 3. The source is hosted on `GitHub
<https://github.com/NiklasRosenstein/myo-python>`_.

There are two ways to use the myo-python bindings: You can either implement
a :class:`myo.DeviceListener` (this is the preferred method as it includes
the least overhead) or you can use the :class:`myo.Feed` object to read the
most recent data when you really need it.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


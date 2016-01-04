
``myo-python`` - Python bindings for the Myo SDK
================================================

.. toctree::
  :caption: Table of Contents

  myo
  myo.utils
  myo.lowlevel


Introduction
------------

This module is a :mod:`ctypes` based wrapper for the Thalmic Myo SDK that
is compatible with Python 2 and 3. The source is hosted on `GitHub
<https://github.com/NiklasRosenstein/myo-python>`_.

There are two ways to use the myo-python bindings: You can either implement
a :class:`myo.DeviceListener` (this is the preferred method as it includes
the least overhead) or you can use the :class:`myo.Feed` object to read the
most recent data when you really need it.

Notifications
-------------

The preferred method to use the Myo SDK is to implement the
:class:`myo.DeviceListener` interface. It defines a number of functions
that will be invoked on various events and when data becomes available.

.. code-block:: python

  from time import sleep
  from myo import Hub, DeviceListener

  class Listener(DeviceListener):

      def on_pair(self, myo, timestamp, firmware_version):
          print("Hello, Myo!")

      def on_unpair(self, myo, timestamp):
          print("Goodbye, Myo!")

      def on_orientation_data(self, myo, timestamp, quat):
          print("Orientation:", quat.x, quat.y, quat.z, quat.w)

  listener = DeviceListener()
  hub = Hub()
  hub.run(1000, listener)

  try:
    while True: sleep(0.5)
  finally:
    hub.shutdown()  # !! crucial

Data Polling
------------

In many cases, it is much easier to just read the most recent data from
a Myo armband when you actually need it. The :class:`myo.Feed` is an
implementation of the :class:`myo.DeviceListener` interface that creates
a :class:`myo.Feed.MyoProxy` object for each connected Myo which always
contains the most recent data. These proxy objects are thread-safe.

.. code-block:: python

  from myo import Hub, Feed

  feed = Feed()
  hub = Hub()
  hub.run(1000, feed)

  try:
    myo = feed.wait_for_single_device(timeout=2.0)
    if not myo:
      print("No Myo connected after 2 seconds")
    print("Hello, Myo!")
    while hub.running and myo.connected:
      quat = myo.orientation
      print('Orientation:', quat.x, quat.y, quat.z, quat.w)
  finally:
    hub.shutdown()  # !! crucial

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Frequently Asked Questions
==========================

.. contents::

OSError: The specified module can not be found
----------------------------------------------

This error occurs on Windows when the ``myo`` dynamic library can not
be found. Did you follow the :ref:`install` Instructions?

OSError: dlopen(myo, 6): image not found
----------------------------------------

This error occurs on Mac OS when the ``myo`` shared library can not
be found. Did you follow the :ref:`install` Instructions?

I don't get any EMG data?
-------------------------

You have to enable EMG streaming first.

.. code:: python

  from myo import StreamEmg
  # ...
  myo_device.set_stream_emg(StreamEmg.enabled)

This applies for :class:`MyoProxy<myo.Feed.MyoProxy>`
as well as for normal :class:`Myo<myo.lowlevel.ctyping.Myo>` objects.

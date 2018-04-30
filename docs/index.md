+++
title = "Home"
renderTitle = false
ordering = 0
+++

  [CFFI]: https://pypi.python.org/pypi/cffi
  [Thalmic Myo SDK]: https://developer.thalmic.com/downloads

# Welcome to the Myo Python Documentation

`myo-python` is a [CFFI] based wrapper around the [Thalmic Myo SDK]. It is
compatible with Python 2.7+ and 3.4+. You can find the source code over at
[GitHub].

## Installation

The Thalmic Myo SDK is only available for Windows and macOS, thus you can not
use `myo-python` on Linux (unfortunately). Use Pip to install the library:

    pip install 'myo-python>=1.0.0'

Next, download the Myo SDK from the [Developer Downloads][Thalmic Myo SDK]
page and extract it so a convenient location.

Finally, you need to make sure that `myo-python` can find the shared library
contained in the Myo SDK. There a multiple ways to do this.

* Add the path to the parent directory of the shared library to your
  `PATH` (Windows) or `DYLD_LIBRARY_PATH` (macOS) environment variable.
  On macOS, to keep the change persistent, add the following line to your
  `~/.bashrc` file: `export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Developer/myo_sdk/myo.framework`

* Pass either `sdk_path`, `bin_path` or `lib_name` to the `myo.init()` function.
  The `bin_path` would be the same as the path that you would add to the
  environment variable.

## Examples

There are a bunch of examples available on the GitHub repository. Check them
out [here](https://github.com/NiklasRosenstein/myo-python/tree/master/examples)!

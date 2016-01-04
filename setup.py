
from setuptools import setup

setup(
  name='myo-python',
  version='0.2.2',
  description='Python bindings for the Thalmic Labs Myo SDK',
  author='Niklas Rosenstein',
  author_email='rosensteinniklas@gmail.com',
  url='https://github.com/NiklasRosenstein/myo-python',
  packages=['myo', 'myo.lowlevel', 'myo.utils'],
  install_requires=['six'],
)

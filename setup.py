
from setuptools import setup

with open('requirements.txt') as fp:
  install_requires = fp.readlines()

setup(
  name='myo-python',
  version='1.0.0',
  description='Python bindings for the Thalmic Labs Myo SDK',
  author='Niklas Rosenstein',
  author_email='rosensteinniklas@gmail.com',
  url='https://github.com/NiklasRosenstein/myo-python',
  packages=['myo', 'myo.types'],
  install_requires=install_requires,
)

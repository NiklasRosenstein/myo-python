
from setuptools import setup

def readme():
  with open('README.md') as fp:
    return fp.read()

setup(
  name='myo-python',
  version='0.2.4',
  description='Python bindings for the Thalmic Labs Myo SDK',
  long_description=readme(),
  long_description_content_type='text/markdown',
  author='Niklas Rosenstein',
  author_email='rosensteinniklas@gmail.com',
  url='https://github.com/NiklasRosenstein/myo-python',
  packages=['myo', 'myo.lowlevel', 'myo.utils'],
  install_requires=['six'],
)

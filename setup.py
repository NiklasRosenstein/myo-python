
from setuptools import setup

with open('README.md') as fp:
  readme = fp.read()

with open('requirements.txt') as fp:
  install_requires = fp.readlines()

setup(
  name='myo-python',
  version='1.0.3',
  description='Python bindings for the Thalmic Labs Myo SDK',
  long_description=readme,
  long_description_content_type='text/markdown',
  author='Niklas Rosenstein',
  author_email='rosensteinniklas@gmail.com',
  license = 'MIT',
  url='https://github.com/NiklasRosenstein/myo-python',
  packages=['myo', 'myo.types'],
  package_data={'myo': ['libmyo.h']},
  install_requires=install_requires,
)

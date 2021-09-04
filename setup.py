
import io
import re
import setuptools
import sys

with io.open('myo/__init__.py', encoding='utf8') as fp:
  version = re.search(r"__version__\s*=\s*'(.*)'", fp.read()).group(1)

with open('README.md') as fp:
  readme = fp.read()

requirements = ['cffi>=1.11.5', 'six>=1.11.0']

setuptools.setup(
  name='myo-python',
  version=version,
  description='Python bindings for the Thalmic Labs Myo SDK',
  long_description=readme,
  long_description_content_type='text/markdown',
  author='Niklas Rosenstein',
  author_email='rosensteinniklas@gmail.com',
  license='MIT',
  url='https://github.com/NiklasRosenstein/myo-python',
  packages=['myo', 'myo.types'],
  package_data={'myo': ['libmyo.h']},
  python_requires = '>=3.5.0,<4.0.0',
  install_requires=requirements,
)

#!/usr/bin/env python

import re
import sys

from setuptools import setup, find_packages


def version():
    with open('reachy/_version.py') as f:
        return re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read()).group(1)


extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(name='reachy',
      version=version(),
      packages=find_packages(),

      install_requires=['pypot >= 2.11', 'poppy-creature >= 1.8'],

      include_package_data=True,
      exclude_package_data={'': ['README', '.gitignore']},

      zip_safe=False,

      author='Pollen Robotics',
      author_email='contact@pollen-robotics.com',
      description='A 7 dof prothesis robotic arm',
      url='https://github.com/pollen-robotics/reachy',

      **extra
      )

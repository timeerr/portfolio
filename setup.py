#!/usr/bin/python3

from setuptools import setup, find_packages

setup(name='portoflio',
      version='0.0.1',
      description='Portfolio tracker',
      url='https://github.com/timeerr/portfolio',
      author='timeerr',
      author_email='timeerr@tuta.io',
      license='MIT',
      packages=find_packages(),
      entry_points={
          'console_scripts': ['portfolio=gui.portfolio:main']
      },
      install_requires=[
          'PyQt5',
          'PyQtChart'
      ],
      zip_safe=False)

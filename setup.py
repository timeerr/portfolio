#!/usr/bin/python3

from setuptools import setup, find_packages


setup(name='portfolio',
      version='0.0.1',
      description='Portfolio tracker',
      url='https://github.com/timeerr/portfolio',
      author='timeerr',
      author_email='timeerr@tuta.io',
      license='MIT',
      packages=find_packages(),
      entry_points={
          'console_scripts': ['portfolio=portfolio.portfolio:main']
      },
      install_requires=[
          'PyQt5 >= 5.13',
          'PyQtChart >= 5.13',
          'QDarkStyle',
          'pandas',
          'openpyxl',
          'appdirs',
          'requests'
      ],
      zip_safe=False)

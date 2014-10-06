#!/usr/bin/env python
"""
Setup script for PAUSE2
"""

from setuptools import setup


setup(name='cpt-pause',
      version='0.1.0',
      description='Pileup Analysis Using Starts and Ends',
      author='Eric Rasche',
      author_email='rasche.eric@yandex.ru',
      url='https://cpt.tamu.edu/gitlab/cpt/pause2/',
      packages=['cpt-pause'],
      license='GPL3',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Operating System :: OS Independent',
          'Intended Audience :: Developers',
          'Environment :: Console'
      ],
      scripts=['bin/pause_analysis.py', 'bin/pause_coverage_to_wiggle.py',
               'bin/pause_plotter.py', 'bin/pause_starts_to_wiggle.py'],
      )

#!/usr/bin/env python
# coding=utf-8
import sys
from copy import copy

from setuptools import setup, find_packages


setup(

    name='pyqtconfig',
    version="0.8.0",
    author='Martin Fitzpatrick',
    author_email='martin.fitzpatrick@gmail.com',
    url='https://github.com/mfitzp/pyqtconfig',
    download_url='https://github.com/mfitzp/pyqtconfig/zipball/master',
    description='An API for keeping PyQt widgets in sync with a config dictionary or QSettings object.',
    long_description='pyqtconfig is a simple API for keeping a config dict in sync with PyQt widgets. \
    Updating the widget automagically updates the dict; updating the dict updates the widget. Internal support \
    for both dictionary config, QSettings and config XML import/export. Combo and list boxes also support \
    mapping from display->internal values.',

    packages = find_packages(),
    include_package_data = True,
    package_data = {
        '': ['*.txt', '*.rst', '*.md'],
    },
    exclude_package_data = { '': ['README.txt'] },

    entry_points = {
        'gui_scripts': [
            'Pathomx = pathomx.Pathomx.main',
        ]
    },
    install_requires = [
            ],

    keywords='bioinformatics research analysis science',
    license='GPL',
    classifiers=['Development Status :: 4 - Beta',
               'Natural Language :: English',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 2',
               'License :: OSI Approved :: BSD License',
               'Topic :: Scientific/Engineering :: Bio-Informatics',
               'Topic :: Education',
               'Intended Audience :: Science/Research',
               'Intended Audience :: Education',
              ],

    options={},
    )

import sys
import setuptools


setuptools.setup(

    name='pyqtconfig',
    version="0.9.0",
    author='Martin Fitzpatrick',
    author_email='martin.fitzpatrick@gmail.com',
    url='https://github.com/learnpyqt/pyqtconfig',
    description='An API for keeping PyQt widgets in sync with a config dictionary or QSettings object.',
    long_description='pyqtconfig is a simple API for keeping a config dict in sync with PyQt widgets. \
    Updating the widget automagically updates the dict; updating the dict updates the widget. Internal support \
    for both dictionary config, QSettings and config XML import/export. Combo and list boxes also support \
    mapping from display->internal values.',
    packages=setuptools.find_packages(),
    keywords='pyqt desktop gui pyqt5 qt',
    license='GPL',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.4',
)

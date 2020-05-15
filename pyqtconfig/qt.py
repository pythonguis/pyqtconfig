# -*- coding: utf-8 -*-
''' This module is a header-like file for pyqtconfig.
'''
from __future__ import unicode_literals
import sys
import os
import importlib

PYSIDE = 0
PYQT4 = 1
PYQT5 = 2

USE_QT_PY = None

QT_API_ENV = os.environ.get('QT_API')
ETS = dict(pyqt=PYQT4, pyqt5=PYQT5, pyside=PYSIDE)

# Check environment variable
if QT_API_ENV and QT_API_ENV in ETS:
    USE_QT_PY = ETS[QT_API_ENV]

# Check if one already importer
elif 'PyQt4' in sys.modules:
    USE_QT_PY = PYQT4
elif 'PyQt5' in sys.modules:
    USE_QT_PY = PYQT5
else:
    # Try importing in turn
    try:
        importlib.import_module('PyQt5')
        USE_QT_PY = PYQT5
    except ImportError:
        try:
            importlib.import_module('PyQt5')
            USE_QT_PY = PYQT4
        except ImportError:
            try:
                importlib.import_module('PyQt5')
                USE_QT_PY = PYSIDE
            except ImportError:
                pass

# Import PyQt classes accessible in elsewhere through from qt import *
if USE_QT_PY == PYQT5:
    from PyQt5.QtCore import (QVariant, Qt, QMutex, QMutexLocker, QSettings,
                              QObject, pyqtSignal)
    from PyQt5.QtWidgets import (QComboBox, QCheckBox, QAction,
                                 QActionGroup, QPushButton, QSpinBox,
                                 QDoubleSpinBox, QPlainTextEdit, QLineEdit,
                                 QListWidget, QSlider, QButtonGroup,
                                 QTabWidget, QApplication, QGridLayout,
                                 QTextEdit, QWidget, QMainWindow)

elif USE_QT_PY == PYSIDE:
    from PySide.QtGui import (QComboBox, QCheckBox, QAction, QMainWindow,
                              QActionGroup, QPushButton, QSpinBox,
                              QDoubleSpinBox, QPlainTextEdit, QLineEdit,
                              QListWidget, QSlider, QButtonGroup, QWidget,
                              QTabWidget, QApplication, QGridLayout, QTextEdit)
    from PySide.QtCore import (Signal, Qt, QMutex, QMutexLocker, QSettings,
                               QObject)

    pyqtSignal = Signal


elif USE_QT_PY == PYQT4:
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4.QtGui import (QComboBox, QCheckBox, QAction, QMainWindow,
                             QActionGroup, QPushButton, QSpinBox,
                             QDoubleSpinBox, QPlainTextEdit, QLineEdit,
                             QListWidget, QSlider, QButtonGroup, QWidget,
                             QTabWidget, QApplication, QGridLayout, QTextEdit)
    from PyQt4.QtCore import (QVariant, Qt, QMutex, QMutexLocker, QSettings,
                              QObject, pyqtSignal)

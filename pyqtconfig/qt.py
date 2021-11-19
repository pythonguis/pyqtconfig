"""
This module is a header-like file for pyqtconfig.

It handles compatibility with PyQt5, PySide2, PyQt6, and PySide6.
"""


import sys

if "PyQt5" in sys.modules:
    Signal = pyqtSignal

    from PyQt5 import QtWidgets
    from PyQt5.QtCore import (
        Qt,
        QMutex,
        QObject,
        QVariant,
        QSettings,
        pyqtSignal,
        QMutexLocker,
    )
    from PyQt5.QtWidgets import (
        QAction,
        QSlider,
        QWidget,
        QSpinBox,
        QCheckBox,
        QComboBox,
        QLineEdit,
        QTextEdit,
        QTabWidget,
        QGridLayout,
        QListWidget,
        QMainWindow,
        QPushButton,
        QActionGroup,
        QButtonGroup,
        QApplication,
        QDoubleSpinBox,
        QPlainTextEdit,
    )

elif "PySide2" in sys.modules:
    QVariant = None

    from PySide2 import QtWidgets
    from PySide2.QtCore import (
        Qt,
        QMutex,
        Signal,
        QObject,
        QSettings,
        QMutexLocker,
    )
    from PySide2.QtWidgets import (
        QAction,
        QSlider,
        QWidget,
        QSpinBox,
        QCheckBox,
        QComboBox,
        QLineEdit,
        QTextEdit,
        QTabWidget,
        QGridLayout,
        QListWidget,
        QMainWindow,
        QPushButton,
        QActionGroup,
        QApplication,
        QButtonGroup,
        QDoubleSpinBox,
        QPlainTextEdit,
    )

elif "PyQt6" in sys.modules:
    Signal = pyqtSignal

    from PyQt6 import QtWidgets
    from PyQt6.QtCore import (
        Qt,
        QMutex,
        QObject,
        QVariant,
        QSettings,
        pyqtSignal,
        QMutexLocker,
    )
    from PyQt6.QtGui import QAction, QActionGroup
    from PyQt6.QtWidgets import (
        QSlider,
        QWidget,
        QSpinBox,
        QCheckBox,
        QComboBox,
        QLineEdit,
        QTextEdit,
        QTabWidget,
        QGridLayout,
        QListWidget,
        QMainWindow,
        QPushButton,
        QApplication,
        QButtonGroup,
        QDoubleSpinBox,
        QPlainTextEdit,
    )

elif "PySide6" in sys.modules:
    QVariant = None

    from PySide6 import QtWidgets
    from PySide6.QtCore import (
        Qt,
        QMutex,
        Signal,
        QObject,
        QSettings,
        QMutexLocker,
    )
    from PySide6.QtGui import QAction, QActionGroup
    from PySide6.QtWidgets import (
        QSlider,
        QWidget,
        QSpinBox,
        QCheckBox,
        QComboBox,
        QLineEdit,
        QTextEdit,
        QTabWidget,
        QGridLayout,
        QListWidget,
        QMainWindow,
        QPushButton,
        QApplication,
        QButtonGroup,
        QDoubleSpinBox,
        QPlainTextEdit,
    )

else:
    raise ImportError("The Qt library must be imported before pyqtconfig.")

"""
This module exists to smooth out some of the differences between PySide, PyQt4 and PyQt5
"""

import sys

PYSIDE = 0
PYQT4 = 1
PYQT5 = 2

USE_QT_PY = None

## Automatically determine whether to use PyQt or PySide. 
## This is done by first checking to see whether one of the libraries
## is already imported. If not, then attempt to import PyQt4, then PySide.
if 'PyQt4' in sys.modules:
    USE_QT_PY = PYQT4
if 'PyQt5' in sys.modules:
    USE_QT_PY = PYQT5
elif 'PySide' in sys.modules:
    USE_QT_PY = PYSIDE
else:
    try:
        import PyQt4
        USE_QT_PY = PYQT4
    except ImportError:
        try:
            import PyQt5
            USE_QT_PY = PYQT5
        except ImportError:
            try:
                import PySide
                USE_QT_PY = PYSIDE
            except:
                pass

if USE_QT_PY == None:
    raise Exception("Requires one of PyQt4, PyQt5 or PySide; none of these packages could be imported.")

if USE_QT_PY == PYSIDE:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtNetwork import *
    
    pyqtSignal = Signal

elif USE_QT_PY == PYQT4:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
    from PyQt4.QtNetwork import *

elif USE_QT_PY == PYQT5:
    
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtNetwork import *
    from PyQt5.QtWidgets import *

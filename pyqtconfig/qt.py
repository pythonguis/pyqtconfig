from __future__ import unicode_literals
import sys
import os
import logging

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
        import PyQt5
        USE_QT_PY = PYQT5
    except:
        try:
            import PyQt4
            USE_QT_PY = PYQT4
        except ImportError:
            try:
                import PySide
                USE_QT_PY = PYSIDE
            except:
                pass

# Import PyQt classes accessible in elsewhere through from qt import *
if USE_QT_PY == PYQT5:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWebKit import *
    from PyQt5.QtNetwork import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtWebKitWidgets import *

elif USE_QT_PY == PYSIDE:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtNetwork import *

    pyqtSignal = Signal


elif USE_QT_PY == PYQT4:
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
    from PyQt4.QtWebKit import *
    from PyQt4.QtNetwork import *

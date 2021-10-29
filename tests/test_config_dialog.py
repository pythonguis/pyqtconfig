

def test_pyqt():
    import sys
    import pytest
    import PyQt5
    from pyqtconfig import ConfigManager, ConfigDialog
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    config = ConfigManager()
    try:
        config_dialog = ConfigDialog(config, cols=2, f=Qt.WindowCloseButtonHint)
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")
    finally:
        sys.modules.pop("PyQt5")
        sys.modules.pop("PyQt5.QtCore")
        sys.modules.pop("PyQt5.QtWidgets")
        sys.modules.pop("PyQt5.sip")
        sys.modules.pop("PyQt5.QtGui")
        sys.modules.pop("pyqtconfig")
        sys.modules.pop("pyqtconfig.config")
        sys.modules.pop("pyqtconfig.qt")

def test_pyside():
    import sys
    import pytest
    import PySide2
    from pyqtconfig import ConfigManager, ConfigDialog
    from PySide2.QtCore import Qt
    from PySide2.QtWidgets import QApplication, QMainWindow
    app = QApplication(sys.argv)
    config = ConfigManager()
    try:
        config_dialog = ConfigDialog(config, cols=2, f=Qt.WindowCloseButtonHint)
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


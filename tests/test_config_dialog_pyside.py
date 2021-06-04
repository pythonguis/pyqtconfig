# import sys
# import pytest
#
#
# def test_pyside():
#     import PySide2
#     from pyqtconfig import ConfigManager, ConfigDialog
#     from PySide2.QtCore import Qt
#     from PySide2.QtWidgets import QApplication
#     app = QApplication(sys.argv)
#     config = ConfigManager()
#     try:
#         config_dialog = ConfigDialog(config, cols=2, f=Qt.WindowCloseButtonHint)
#     except Exception as e:
#         pytest.fail(f"Unexpected exception: {e}")
#     finally:
#         app.deleteLater()
#         del PySide2.QtCore.Qt
#         del PySide2.QtWidgets.QApplication
#         del PySide2

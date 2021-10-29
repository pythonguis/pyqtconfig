import sys
import pytest

from PyQt5.QtWidgets import QApplication
from pyqtconfig import QSettingsManager


def test_no_appname():
    with pytest.warns(None) as record:
        app = QApplication(sys.argv)
        conf = QSettingsManager()
    assert len(record) == 1


def test_no_appname_no_warn():
        with pytest.warns(None) as record:
            app = QApplication(sys.argv)
            conf = QSettingsManager(warn_no_app_name=False)
        assert len(record) == 0


def test_yes_appname():
    with pytest.warns(None) as record:
        app = QApplication(sys.argv)
        app.setOrganizationName("TestPyQtConfig")
        app.setApplicationName("TestPyQtConfig")
        conf = QSettingsManager()
    assert len(record) == 0

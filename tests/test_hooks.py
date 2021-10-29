"""
    test_config.py Copyright © 2015 by Stefan Lehmann

    Test assignment of hooks.

"""
import sys
import pytest

from PyQt5.QtWidgets import QLineEdit, QApplication
from pyqtconfig import ConfigManager
from pyqtconfig.config import _get_QLineEdit, _set_QLineEdit, _event_QLineEdit

app = QApplication(sys.argv)


def test_hook_direct():
    widget = QLineEdit()
    config = ConfigManager()
    assert config._get_hook(widget) == QLineEdit

def test_hook_inherited():
    class MyLineEdit(QLineEdit):
        pass

    widget = MyLineEdit()
    config = ConfigManager()
    assert config._get_hook(widget) == QLineEdit

def test_hook_inherited_direct():
    class MyLineEdit(QLineEdit):
        pass

    widget = MyLineEdit()
    config = ConfigManager()
    config.add_hooks(MyLineEdit, (_get_QLineEdit, _set_QLineEdit, _event_QLineEdit))
    assert config._get_hook(widget) == MyLineEdit

def test_no_hook():
    class MyTestClass:
        pass
    o = MyTestClass()
    config = ConfigManager()
    with pytest.raises(TypeError) as e:
        assert config._get_hook(o)
    assert "No handler-functions available for this" in str(e)


app.deleteLater()
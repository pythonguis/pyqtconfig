pyqtconfig
==========

pyqtconfig is a simple API for keeping a config dict in sync with PyQt widgets.
Updating the widget automagically updates the dict; updating the dict updates the widget. Internal support
for both dictionary config, QSettings and config XML import/export. Combo and list boxes also support
mapping from display->internal values.

Usage of QSettings dict:

    settings = QSettingsManager()

    settings.set('demo/number', 42)
    settings.set('demo/text', "bla")
    settings.set('demo/array', ["a", "b"])

    print settings.get('demo/number')

    lineEdit = QtGui.QLineEdit()
    settings.add_handler('demo/textfield', lineEdit)
    checkbox = QtGui.QCheckBox('active')
    settings.add_handler('demo/active', checkbox)

pyqtconfig
==========

pyqtconfig is a simple API for keeping a config dict in sync with PyQt widgets.
Updating the widget automagically updates the dict; updating the dict updates the widget. Internal support
for both dictionary config, QSettings and config XML import/export. Combo and list boxes also support
mapping from display->internal values.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

# Import PyQt5 classes
from .qt import *

import os
import sys
import numpy as np
import types

from collections import defaultdict, OrderedDict
import operator
import logging

try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et

RECALCULATE_ALL = 1
RECALCULATE_VIEW = 2


def types_MethodType(fn, handler):
    try:
        return types.MethodType(fn, handler, type(handler))
    except TypeError:
        return types.MethodType(fn, handler)


def _convert_list_type_from_XML(vs):
    '''
    Lists are a complex type with possibility for mixed sub-types. Therefore each
    sub-entity must be wrapped with a type specifier.
    '''
    vlist = vs.findall('ListItem') + vs.findall('ConfigListItem')  # ConfigListItem is legacy
    l = []
    for xconfig in vlist:
        v = xconfig.text
        if xconfig.get('type') in CONVERT_TYPE_FROM_XML:
            # Recursive; woo!
            v = CONVERT_TYPE_FROM_XML[xconfig.get('type')](xconfig)
        l.append(v)
    return l


def _convert_list_type_to_XML(co, vs):
    '''
    Lists are a complex type with possibility for mixed sub-types. Therefore each
    sub-entity must be wrapped with a type specifier.
    '''
    for cv in vs:
        c = et.SubElement(co, "ListItem")
        t = type(cv).__name__
        c.set("type", t)
        c = CONVERT_TYPE_TO_XML[t](c, cv)
    return co


def _convert_dict_type_from_XML(vs):
    '''
    Dicts are a complex type with possibility for mixed sub-types. Therefore each
    sub-entity must be wrapped with a type specifier.
    '''
    vlist = vs.findall('DictItem')
    d = {}
    for xconfig in vlist:
        v = xconfig.text
        if xconfig.get('type') in CONVERT_TYPE_FROM_XML:
            # Recursive; woo!
            v = CONVERT_TYPE_FROM_XML[xconfig.get('type')](xconfig)
        d[xconfig.get('key')] = v
    return d


def _convert_dict_type_to_XML(co, vs):
    '''
    Dicts are a complex type with possibility for mixed sub-types. Therefore each
    sub-entity must be wrapped with a type specifier.
    '''
    for k, v in vs.items():
        c = et.SubElement(co, "DictItem")
        t = type(v).__name__
        c.set("type", t)
        c.set("key", k)
        c = CONVERT_TYPE_TO_XML[t](c, v)
    return co


def _apply_text_str(co, s):
    co.text = str(s)
    return co

CONVERT_TYPE_TO_XML = {
    'str': _apply_text_str,
    'unicode': _apply_text_str,
    'int': _apply_text_str,
    'float': _apply_text_str,
    'bool': _apply_text_str,
    'list': _convert_list_type_to_XML,
    'tuple': _convert_list_type_to_XML,
    'dict': _convert_dict_type_to_XML,
    'NoneType': _apply_text_str,
}

CONVERT_TYPE_FROM_XML = {
    'str': lambda x: str(x.text),
    'unicode': lambda x: str(x.text),
    'int': lambda x: int(x.text),
    'float': lambda x: float(x.text),
    'bool': lambda x: bool(x.text.lower() == 'true'),
    'list': _convert_list_type_from_XML,
    'tuple': _convert_list_type_from_XML,
    'dict': _convert_dict_type_from_XML,
    'NoneType': lambda x: None,
}


def build_dict_mapper(mdict):
    '''
    Build a map function pair for forward and reverse mapping from a specified dict
    
    Mapping requires both a forward and reverse (get, set) mapping function. This function
    is used to automatically convert a supplied dict to a forward and reverse paired lambda.
    
    :param mdict: A dictionary of display values (keys) and stored values (values)
    :type mdict: dict
    :rtype: 2-tuple of lambdas that perform forward and reverse map
                
    '''
    rdict = {v: k for k, v in mdict.items()}
    return (
        lambda x: mdict[x] if x in mdict else x,
        lambda x: rdict[x] if x in rdict else x,
        )

try:
    # Python2.7
    unicode
except:


    # Python3 recoding
    def unicode(s):
        if isinstance(s, bytes):
            return s.decode('utf-8')
        else:
            return s


def build_tuple_mapper(mlist):
    '''
    Build a map function pair for forward and reverse mapping from a specified list of tuples
    
    :param mlist: A list of tuples of display values (keys) and stored values (values)
    :type mlist: list-of-tuples
    :rtype: 2-tuple of lambdas that perform forward and reverse map
                
    '''
    rdict = {v: k for k, v in mlist}
    return (
        lambda x: mdict[x] if x in mdict else x,
        lambda x: rdict[x] if x in rdict else x,
        )


# CUSTOM HANDLERS

# QComboBox
def _get_QComboBox(self):
    """
        Get value QCombobox via re-mapping filter
    """
    return self._get_map(self.currentText())


def _set_QComboBox(self, v):
    """
        Set value QCombobox via re-mapping filter
    """
    self.setCurrentIndex(self.findText(unicode(self._set_map(v))))


def _event_QComboBox(self):
    """
        Return QCombobox change event signal
    """
    return self.currentIndexChanged


# QCheckBox
def _get_QCheckBox(self):
    """
        Get state of QCheckbox
    """
    return self.isChecked()


def _set_QCheckBox(self, v):
    """
        Set state of QCheckbox
    """
    self.setChecked(v)


def _event_QCheckBox(self):
    """
        Return state change signal for QCheckbox
    """
    return self.stateChanged


# QAction
def _get_QAction(self):
    """
        Get checked state of QAction
    """
    return self.isChecked()


def _set_QAction(self, v):
    """
        Set checked state of QAction
    """
    self.setChecked(v)


def _event_QAction(self):
    """
        Return state change signal for QAction
    """
    return self.toggled


# QActionGroup
def _get_QActionGroup(self):
    """
        Get checked state of QAction
    """
    if self.checkedAction():
        return self.actions().index(self.checkedAction())
    else:
        return None


def _set_QActionGroup(self, v):
    """
        Set checked state of QAction
    """
    self.actions()[v].setChecked(True)


def _event_QActionGroup(self):
    """
        Return state change signal for QAction
    """
    return self.triggered


# QPushButton
def _get_QPushButton(self):
    """
        Get checked state of QPushButton
    """
    return self.isChecked()


def _set_QPushButton(self, v):
    """
        Set checked state of QPushButton
    """
    self.setChecked(v)


def _event_QPushButton(self):
    """
        Return state change signal for QPushButton
    """
    return self.toggled


# QSpinBox
def _get_QSpinBox(self):
    """
        Get current value for QSpinBox
    """
    return self.value()


def _set_QSpinBox(self, v):
    """
        Set current value for QSpinBox
    """
    self.setValue(v)


def _event_QSpinBox(self):
    """
        Return value change signal for QSpinBox
    """
    return self.valueChanged


# QDoubleSpinBox
def _get_QDoubleSpinBox(self):
    """
        Get current value for QDoubleSpinBox
    """
    return self.value()


def _set_QDoubleSpinBox(self, v):
    """
        Set current value for QDoubleSpinBox
    """
    self.setValue(v)


def _event_QDoubleSpinBox(self):
    """
        Return value change signal for QDoubleSpinBox
    """
    return self.valueChanged


# QPlainTextEdit
def _get_QPlainTextEdit(self):
    """
        Get current document text for QPlainTextEdit
    """
    return self.document().toPlainText()


def _set_QPlainTextEdit(self, v):
    """
        Set current document text for QPlainTextEdit
    """
    self.setPlainText(unicode(v))


def _event_QPlainTextEdit(self):
    """
        Return current value changed signal for QPlainTextEdit box.
        
        Note that this is not a native Qt signal but a signal manually fired on 
        the user's pressing the "Apply changes" to the code button. Attaching to the 
        modified signal would trigger recalculation on every key-press.
    """
    return self.sourceChangesApplied


# QLineEdit
def _get_QLineEdit(self):
    """
        Get current text for QLineEdit
    """
    return self._get_map(self.text())


def _set_QLineEdit(self, v):
    """
        Set current text for QLineEdit
    """
    self.setText(unicode(self._set_map(v)))


def _event_QLineEdit(self):
    """
        Return current value changed signal for QLineEdit box.
    """
    return self.textChanged


# CodeEditor
def _get_CodeEditor(self):
    """
        Get current document text for CodeEditor. Wraps _get_QPlainTextEdit.
    """
    _get_QPlainTextEdit(self)


def _set_CodeEditor(self, v):
    """
        Set current document text for CodeEditor. Wraps _set_QPlainTextEdit.
    """
    _set_QPlainTextEdit(self, unicode(v))


def _event_CodeEditor(self):
    """
        Return current value changed signal for CodeEditor box. Wraps _event_QPlainTextEdit.
    """
    return _event_QPlainTextEdit(self)


# QListWidget
def _get_QListWidget(self):
    """
        Get currently selected values in QListWidget via re-mapping filter.
        
        Selected values are returned as a list.
    """
    return [self._get_map(s.text()) for s in self.selectedItems()]


def _set_QListWidget(self, v):
    """
        Set currently selected values in QListWidget via re-mapping filter.
        
        Supply values to be selected as a list.
    """
    if v:
        for s in v:
            self.findItems(unicode(self._set_map(s)), Qt.MatchExactly)[0].setSelected(True)


def _event_QListWidget(self):
    """
        Return current selection changed signal for QListWidget.
    """
    return self.itemSelectionChanged


# QListWidgetWithAddRemoveEvent
def _get_QListWidgetAddRemove(self):
    """
        Get current values in QListWidget via re-mapping filter.
        
        Selected values are returned as a list.
    """
    return [self._get_map(self.item(n).text()) for n in range(0, self.count())]


def _set_QListWidgetAddRemove(self, v):
    """
        Set currently values in QListWidget via re-mapping filter.
        
        Supply values to be selected as a list.
    """
    block = self.blockSignals(True)
    self.clear()
    self.addItems([unicode(self._set_map(s)) for s in v])
    self.blockSignals(block)
    self.itemAddedOrRemoved.emit()


def _event_QListWidgetAddRemove(self):
    """
        Return current selection changed signal for QListWidget.
    """
    return self.itemAddedOrRemoved


# QColorButton
def _get_QColorButton(self):
    """
        Get current value for QColorButton
    """
    return self.color()


def _set_QColorButton(self, v):
    """
        Set current value for QColorButton
    """
    self.setColor(v)


def _event_QColorButton(self):
    """
        Return value change signal for QColorButton
    """
    return self.colorChanged


# QNoneDoubleSpinBox
def _get_QNoneDoubleSpinBox(self):
    """
        Get current value for QDoubleSpinBox
    """
    return self.value()


def _set_QNoneDoubleSpinBox(self, v):
    """
        Set current value for QDoubleSpinBox
    """
    self.setValue(v)


def _event_QNoneDoubleSpinBox(self):
    """
        Return value change signal for QDoubleSpinBox
    """
    return self.valueChanged


#QCheckTreeWidget
def _get_QCheckTreeWidget(self):
    """
        Get currently checked values in QCheckTreeWidget via re-mapping filter.
        
        Selected values are returned as a list.
    """
    return [self._get_map(s) for s in self._checked_item_cache]


def _set_QCheckTreeWidget(self, v):
    """
        Set currently checked values in QCheckTreeWidget via re-mapping filter.
        
        Supply values to be selected as a list.
    """
    if v:
        for s in v:
            f = self.findItems(unicode(self._set_map(s)), Qt.MatchExactly | Qt.MatchRecursive)
            if f:
                f[0].setCheckState(0, Qt.Checked)


def _event_QCheckTreeWidget(self):
    """
        Return current checked changed signal for QCheckTreeWidget.
    """
    return self.itemCheckedChanged

HOOKS = {
    'QComboBox': (_get_QComboBox, _set_QComboBox, _event_QComboBox),
    'QCheckBox': (_get_QCheckBox, _set_QCheckBox, _event_QCheckBox),
    'QAction': (_get_QAction, _set_QAction, _event_QAction),
    'QActionGroup': (_get_QActionGroup, _set_QActionGroup, _event_QActionGroup),
    'QPushButton': (_get_QPushButton, _set_QPushButton, _event_QPushButton),
    'QSpinBox': (_get_QSpinBox, _set_QSpinBox, _event_QSpinBox),
    'QDoubleSpinBox': (_get_QDoubleSpinBox, _set_QDoubleSpinBox, _event_QDoubleSpinBox),
    'QPlainTextEdit': (_get_QPlainTextEdit, _set_QPlainTextEdit, _event_QPlainTextEdit),
    'QLineEdit': (_get_QLineEdit, _set_QLineEdit, _event_QLineEdit),
    'CodeEditor': (_get_CodeEditor, _set_CodeEditor, _event_CodeEditor),
    'QListWidget': (_get_QListWidget, _set_QListWidget, _event_QListWidget),
    'QListWidgetAddRemove': (_get_QListWidgetAddRemove, _set_QListWidgetAddRemove, _event_QListWidgetAddRemove),
    'QColorButton': (_get_QColorButton, _set_QColorButton, _event_QColorButton),
    'QNoneDoubleSpinBox': (_get_QNoneDoubleSpinBox, _set_QNoneDoubleSpinBox, _event_QNoneDoubleSpinBox),
    'QCheckTreeWidget': (_get_QCheckTreeWidget, _set_QCheckTreeWidget, _event_QCheckTreeWidget),
}


# ConfigManager handles configuration for a given appview
# Supports default values, change signals, export/import from file (for workspace saving)
class ConfigManagerBase(QObject):

    # Signals
    updated = pyqtSignal(int)  # Triggered anytime configuration is changed (refresh)

    def __init__(self, defaults={}, *args, **kwargs):
        super(ConfigManagerBase, self).__init__(*args, **kwargs)

        self.mutex = QMutex()
        self.hooks = HOOKS
        self.reset()
        self.defaults = defaults  # Same mapping as above, used when config not set

    def _get(self, key):
        with QMutexLocker(self.mutex):
            try:
                return self.config[key]
            except:
                return None

    def _get_default(self, key):
        with QMutexLocker(self.mutex):
            try:
                return self.defaults[key]
            except:
                return None

    # Get config
    def get(self, key):
        """ 
            Get config value for a given key from the config manager.
            
            Returns the value that matches the supplied key. If the value is not set a
            default value will be returned as set by set_defaults.
            
            :param key: The configuration key to return a config value for
            :type key: str
            :rtype: Any supported (str, int, bool, list-of-supported-types)
        """
        v = self._get(key)
        if v is not None:
            return v
        else:
            return self._get_default(key)

    def set(self, key, value, trigger_handler=True, trigger_update=True):
        """ 
            Set config value for a given key in the config manager.
            
            Set key to value. The optional trigger_update determines whether event hooks
            will fire for this key (and so re-calculation). It is useful to suppress these
            when updating multiple values for example.
            
            :param key: The configuration key to set
            :type key: str
            :param value: The value to set the configuration key to
            :type value: Any supported (str, int, bool, list-of-supported-types)
            :rtype: bool (success)   
        """
        if self._get(key) == value:
            return False  # Not updating

        # Set value
        self._set(key, value)

        if trigger_handler and key in self.handlers:
            # Trigger handler to update the view
            getter = self.handlers[key].getter
            setter = self.handlers[key].setter

            if setter and getter() != self._get(key):
                setter(self._get(key))

        # Trigger update notification
        if trigger_update:
            self.updated.emit(self.eventhooks[key] if key in self.eventhooks else RECALCULATE_ALL)

        return True

    # Defaults are used in absence of a set value (use for base settings)
    def set_default(self, key, value, eventhook=RECALCULATE_ALL):
        """
        Set the default value for a given key.
        
        This will be returned if the value is 
        not set in the current config. It is important to include defaults for all 
        possible config values for backward compatibility with earlier versions of a plugin.
        
        :param key: The configuration key to set
        :type key: str
        :param value: The value to set the configuration key to
        :type value: Any supported (str, int, bool, list-of-supported-types)
        :param eventhook: Attach either a full recalculation trigger (default), or a view-only recalculation trigger to these values.
        :type eventhook: int RECALCULATE_ALL, RECALCULATE_VIEWS
        
        """

        self.defaults[key] = value
        self.eventhooks[key] = eventhook
        self.updated.emit(eventhook)

    def set_defaults(self, keyvalues, eventhook=RECALCULATE_ALL):
        """
        Set the default value for a set of keys.
        
        These will be returned if the value is 
        not set in the current config. It is important to include defaults for all 
        possible config values for backward compatibility with earlier versions of a plugin.
        
        :param keyvalues: A dictionary of keys and values to set as defaults
        :type key: dict
        :param eventhook: Attach either a full recalculation trigger (default), or a view-only recalculation trigger to these values.
        :type eventhook: int RECALCULATE_ALL, RECALCULATE_VIEWS
        
        """
        for key, value in list(keyvalues.items()):
            self.defaults[key] = value
            self.eventhooks[key] = eventhook

        # Updating the defaults may update the config (if anything without a config value
        # is set by it; should check)
        self.updated.emit(eventhook)
    # Completely replace current config (wipe all other settings)

    def replace(self, keyvalues, trigger_update=True):
        """
        Completely reset the config with a set of key values.
        
        Note that this does not wipe handlers or triggers (see reset), it simply replaces the values
        in the config entirely. It is the equivalent of unsetting all keys, followed by a
        set_many. Anything not in the supplied keyvalues will revert to default.
        
        :param keyvalues: A dictionary of keys and values to set as defaults
        :type keyvalues: dict
        :param trigger_update: Flag whether to trigger a config update (+recalculation) after all values are set. 
        :type trigger_update: bool
        
        """
        self.config = []
        self.set_many(keyvalues)

    def set_many(self, keyvalues, trigger_update=True):
        """
        Set the value of multiple config settings simultaneously.
        
        This postpones the 
        triggering of the update signal until all values are set to prevent excess signals.
        The trigger_update option can be set to False to prevent any update at all.
            
        :param keyvalues: A dictionary of keys and values to set.
        :type key: dict
        :param trigger_update: Flag whether to trigger a config update (+recalculation) after all values are set. 
        :type trigger_update: bool
        """
        has_updated = False
        for k, v in list(keyvalues.items()):
            u = self.set(k, v, trigger_update=False)
            has_updated = has_updated or u

        if has_updated and trigger_update:
            self.updated.emit(RECALCULATE_ALL)

        return has_updated
    # HANDLERS

    # Handlers are UI elements (combo, select, checkboxes) that automatically update
    # and updated from the config manager. Allows instantaneous updating on config
    # changes and ensuring that elements remain in sync

    def add_handler(self, key, handler, mapper=(lambda x: x, lambda x: x), auto_set_default=True):
        """
        Add a handler (UI element) for a given config key.
        
        The supplied handler should be a QWidget or QAction through which the user
        can change the config setting. An automatic getter, setter and change-event
        handler is attached which will keep the widget and config in sync. The attached
        handler will default to the correct value from the current config.
        
        An optional mapper may also be provider to handler translation from the values
        shown in the UI and those saved/loaded from the config.

        """
        # Add map handler for converting displayed values to internal config data
        if type(mapper) == dict or type(mapper) == OrderedDict:  # By default allow dict types to be used
            mapper = build_dict_mapper(mapper)

        elif type(mapper) == list and type(mapper[0]) == tuple:
            mapper = build_tuple_mapper(mapper)

        handler._get_map, handler._set_map = mapper

        if key in self.handlers:  # Already there; so skip must remove first to replace
            return

        self.handlers[key] = handler

        if type(handler).__name__  not in self.hooks:
            assert False, "No handler-functions available for this widget type (%s)" % type(handler).__name__
           
        hookg, hooks, hooku = self.hooks[type(handler).__name__]

        handler.getter = types_MethodType(hookg, handler)
        handler.setter = types_MethodType(hooks, handler)
        handler.updater = types_MethodType(hooku, handler)

        logging.debug("Add handler %s for %s" % (type(handler).__name__, key))
        handler_callback = lambda x = None: self.set(key, handler.getter(), trigger_handler=False)
        handler.updater().connect(handler_callback)

        # Store this so we can issue a specific remove on deletes
        self.handler_callbacks[key] = handler_callback

        # If the key is not in defaults, set the default to match the handler
        if key not in self.defaults:
            self.set_default(key, handler.getter())

        # Keep handler and data consistent
        if self._get(key) is not None:
            handler.setter(self._get(key))

        # If the key is in defaults; set the handler to the default state (but don't add to config)
        elif key in self.defaults:
            handler.setter(self.defaults[key])

    def add_handlers(self, keyhandlers):
        for key, handler in list(keyhandlers.items()):
            self.add_handler(key, handler)

    def remove_handler(self, key):
        if key in self.handlers:
            handler = self.handlers[key]
            handler.updater().disconnect(self.handler_callbacks[key])
            del self.handlers[key]

    def add_hooks(self, key, hooks):
        self.hooks[key] = hooks

    def getXMLConfig(self, root):
        config = et.SubElement(root, "Config")
        for ck, cv in list(self.config.items()):
            co = et.SubElement(config, "ConfigSetting")
            co.set("id", ck)
            t = type(cv).__name__
            co.set("type", type(cv).__name__)
            co = CONVERT_TYPE_TO_XML[t](co, cv)

        return root

    def setXMLConfig(self, root):

        config = {}
        for xconfig in root.findall('Config/ConfigSetting'):
            #id="experiment_control" type="unicode" value="monocyte at intermediate differentiation stage (GDS2430_2)"/>
            if xconfig.get('type') in CONVERT_TYPE_FROM_XML:
                v = CONVERT_TYPE_FROM_XML[xconfig.get('type')](xconfig)
            config[xconfig.get('id')] = v

        self.set_many(config, trigger_update=False)

    def as_dict(self):
        '''
        Return the combination of defaults and config as a flat dict (so it can be pickled)
        '''
        result_dict = {}
        for k, v in self.defaults.items():
            result_dict[k] = self.get(k)

        return result_dict

    
class ConfigManager(ConfigManagerBase):

    def reset(self):
        """ 
            Reset the config manager to it's initialised state.
            
            This clears all values, unsets all defaults and removes all handlers, maps, and hooks.
        """
        self.config = {}
        self.handlers = {}
        self.handler_callbacks = {}
        self.defaults = {}
        self.maps = {}
        self.eventhooks = {}
        
    def _get(self, key):
        with QMutexLocker(self.mutex):
            try:
                return self.config[key]
            except:
                return None

    def _set(self, key, value):
        with QMutexLocker(self.mutex):
            self.config[key] = value


class QSettingsManager(ConfigManagerBase):

    def reset(self):
        """ 
            Reset the config manager to it's initialised state.
            
            This initialises QSettings, unsets all defaults and removes all handlers, maps, and hooks.
        """
        self.settings = QSettings()
        self.handlers = {}
        self.handler_callbacks = {}
        self.defaults = {}
        self.maps = {}
        self.eventhooks = {}

    def _get(self, key):
        with QMutexLocker(self.mutex):

            v = self.settings.value(key, None)
            if v is not None:
                if type(v) == QVariant and v.type() == QVariant.Invalid:  # Invalid check for Qt4
                    return None

                # Map type to that in defaults: required in case QVariant is a string
                # representation of the actual value (e.g. on Windows Reg)
                vt = type(v)
                if key in self.defaults:
                    dt = type(self.defaults[key])
                    if vt == QVariant:
                        # The target type is a QVariant so munge it
                        # If QVariant (Qt4):
                        type_munge = {
                            int: v.toInt,
                            float: v.toFloat,
                            str: v.toString,
                            unicode: v.toString,
                            bool: v.toBool,
                            list: v.toStringList,
                        }
                        v = type_munge[dt]()
                    elif vt != dt and vt == unicode:
                        # Value is stored as unicode so munge it
                        type_munge = {
                            int: lambda x: int(x),
                            float: lambda x: float(x),
                            str: lambda x: str(x),
                            bool: lambda x: x.lower() == u'true',
                            # other types?
                        }
                        v = type_munge[dt](v)

                    v = dt(v)

                return v

            else:
                return None

    def _set(self, key, value):
        with QMutexLocker(self.mutex):
            self.settings.setValue(key, value)

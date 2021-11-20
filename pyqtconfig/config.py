"""
pyqtconfig is a simple API for handling, persisting, and synchronising a
configuration within PyQt/PySide applications.
"""


import os
import sys
import enum
import json
import math
import types
import logging
import pathlib
import warnings
import collections
import xml.etree.ElementTree as ET

from .qt import (
    Qt,
    QMutex,
    Signal,
    QAction,
    QObject,
    QSlider,
    QSpinBox,
    QVariant,
    QCheckBox,
    QComboBox,
    QLineEdit,
    QSettings,
    QtWidgets,
    QTabWidget,
    QListWidget,
    QPushButton,
    QActionGroup,
    QApplication,
    QButtonGroup,
    QMutexLocker,
    QDoubleSpinBox,
    QPlainTextEdit,
)


def _method_type(fn, handler):
    try:
        return types.MethodType(fn, handler, type(handler))
    except TypeError:
        return types.MethodType(fn, handler)


def _convert_list_type_from_XML(vs):
    """
    The list is a complex type with possibility for mixed sub-types.

    Therefore, each sub-entity must be wrapped with a type specifier.
    """
    vlist = vs.findall("ListItem") + vs.findall("ConfigListItem")
    l = []
    for xconfig in vlist:
        v = xconfig.text
        if xconfig.get("type") in CONVERT_TYPE_FROM_XML:
            # Recursive.
            v = CONVERT_TYPE_FROM_XML[xconfig.get("type")](xconfig)
        l.append(v)
    return l


def _convert_list_type_to_XML(co, vs):
    """
    The list is a complex type with possibility for mixed sub-types.

    Therefore, each sub-entity must be wrapped with a type specifier.
    """
    for cv in vs:
        c = ET.SubElement(co, "ListItem")
        t = type(cv).__name__
        c.set("type", t)
        c = CONVERT_TYPE_TO_XML[t](c, cv)
    return co


def _convert_dict_type_from_XML(vs):
    """
    The dict is a complex type with possibility for mixed sub-types.

    Therefore, each sub-entity must be wrapped with a type specifier.
    """
    vlist = vs.findall("DictItem")
    d = {}
    for xconfig in vlist:
        v = xconfig.text
        if xconfig.get("type") in CONVERT_TYPE_FROM_XML:
            # Recursive.
            v = CONVERT_TYPE_FROM_XML[xconfig.get("type")](xconfig)
        d[xconfig.get("key")] = v
    return d


def _convert_dict_type_to_XML(co, vs):
    """
    The dict is a complex type with possibility for mixed sub-types.

    Therefore, each sub-entity must be wrapped with a type specifier.
    """
    for k, v in vs.items():
        c = ET.SubElement(co, "DictItem")
        t = type(v).__name__
        c.set("type", t)
        c.set("key", k)
        c = CONVERT_TYPE_TO_XML[t](c, v)
    return co


def _apply_text_str(co, s):
    co.text = str(s)
    return co


CONVERT_TYPE_TO_XML = {
    "str": _apply_text_str,
    "unicode": _apply_text_str,
    "int": _apply_text_str,
    "float": _apply_text_str,
    "bool": _apply_text_str,
    "list": _convert_list_type_to_XML,
    "tuple": _convert_list_type_to_XML,
    "dict": _convert_dict_type_to_XML,
    "NoneType": _apply_text_str,
}

CONVERT_TYPE_FROM_XML = {
    "str": lambda x: str(x.text),
    "unicode": lambda x: str(x.text),
    "int": lambda x: int(x.text),
    "float": lambda x: float(x.text),
    "bool": lambda x: bool(x.text.lower() == "true"),
    "list": _convert_list_type_from_XML,
    "tuple": _convert_list_type_from_XML,
    "dict": _convert_dict_type_from_XML,
    "NoneType": lambda x: None,
}


def build_dict_mapper(mdict):
    """
    Build a map function pair for forward and reverse mapping from a
    specified dict.

    A mapping requires both a forward and a reverse (get, set) mapping
    function. This function is used to automatically convert a supplied
    dict to a forward and a reverse paired lambda.

    :param mdict: A dictionary of keys and values
    :type mdict: dict
    :rtype: 2-tuple of lambdas that perform forward and reverse mappings

    """
    rdict = {v: k for k, v in mdict.items()}
    return (
        lambda x: mdict[x] if x in mdict else x,
        lambda x: rdict[x] if x in rdict else x,
    )


def unicode(s):
    if isinstance(s, bytes):
        return s.decode("utf-8")
    return s


def build_tuple_mapper(mlist):
    """
    Build a map function pair for forward and reverse mapping from a
    specified list of tuples.

    :param mlist: A list of tuples
    :type mlist: list of tuples
    :rtype: 2-tuple of lambdas that perform forward and reverse mappings
    """
    rdict = {v: k for k, v in mlist}
    return (
        lambda x: mlist[x] if x in mlist else x,
        lambda x: rdict[x] if x in rdict else x,
    )


# CUSTOM HANDLERS

# QComboBox
def _get_QComboBox(self):
    return self._get_map(self.currentText())


def _set_QComboBox(self, v):
    self.setCurrentIndex(self.findText(unicode(self._set_map(v))))


def _event_QComboBox(self):
    return self.currentIndexChanged


# QCheckBox
def _get_QCheckBox(self):
    return self.isChecked()


def _set_QCheckBox(self, v):
    self.setChecked(v)


def _event_QCheckBox(self):
    return self.stateChanged


# QAction
def _get_QAction(self):
    return self.isChecked()


def _set_QAction(self, v):
    self.setChecked(v)


def _event_QAction(self):
    return self.toggled


# QActionGroup
def _get_QActionGroup(self):
    if self.checkedAction():
        return self.actions().index(self.checkedAction())
    return None


def _set_QActionGroup(self, v):
    self.actions()[v].setChecked(True)


def _event_QActionGroup(self):
    return self.triggered


# QPushButton
def _get_QPushButton(self):
    return self.isChecked()


def _set_QPushButton(self, v):
    self.setChecked(v)


def _event_QPushButton(self):
    return self.toggled


# QSpinBox
def _get_QSpinBox(self):
    return self.value()


def _set_QSpinBox(self, v):
    self.setValue(v)


def _event_QSpinBox(self):
    return self.valueChanged


# QDoubleSpinBox
def _get_QDoubleSpinBox(self):
    return self.value()


def _set_QDoubleSpinBox(self, v):
    self.setValue(v)


def _event_QDoubleSpinBox(self):
    return self.valueChanged


# QPlainTextEdit
def _get_QPlainTextEdit(self):
    return self.document().toPlainText()


def _set_QPlainTextEdit(self, v):
    self.setPlainText(unicode(v))


def _event_QPlainTextEdit(self):
    return self.textChanged


# QLineEdit
def _get_QLineEdit(self):
    return self._get_map(self.text())


def _set_QLineEdit(self, v):
    self.setText(unicode(self._set_map(v)))


def _event_QLineEdit(self):
    return self.textChanged


# CodeEditor
def _get_CodeEditor(self):
    _get_QPlainTextEdit(self)


def _set_CodeEditor(self, v):
    _set_QPlainTextEdit(self, unicode(v))


def _event_CodeEditor(self):
    return _event_QPlainTextEdit(self)


# QListWidget
def _get_QListWidget(self):
    return [self._get_map(s.text()) for s in self.selectedItems()]


def _set_QListWidget(self, v):
    if v:
        for s in v:
            self.findItems(
                unicode(self._set_map(s)),
                Qt.MatchExactly
            )[0].setSelected(True)


def _event_QListWidget(self):
    return self.itemSelectionChanged


# QListWidgetWithAddRemoveEvent
def _get_QListWidgetAddRemove(self):
    return [self._get_map(self.item(n).text()) for n in range(self.count())]


def _set_QListWidgetAddRemove(self, v):
    block = self.blockSignals(True)
    self.clear()
    self.addItems([unicode(self._set_map(s)) for s in v])
    self.blockSignals(block)
    self.itemAddedOrRemoved.emit()


def _event_QListWidgetAddRemove(self):
    return self.itemAddedOrRemoved


# QColorButton
def _get_QColorButton(self):
    return self.color()


def _set_QColorButton(self, v):
    self.setColor(v)


def _event_QColorButton(self):
    return self.colorChanged


# QNoneDoubleSpinBox
def _get_QNoneDoubleSpinBox(self):
    return self.value()


def _set_QNoneDoubleSpinBox(self, v):
    self.setValue(v)


def _event_QNoneDoubleSpinBox(self):
    return self.valueChanged


# QCheckTreeWidget
def _get_QCheckTreeWidget(self):
    return [self._get_map(s) for s in self._checked_item_cache]


def _set_QCheckTreeWidget(self, v):
    if v:
        for s in v:
            f = self.findItems(
                unicode(self._set_map(s)),
                Qt.MatchExactly | Qt.MatchRecursive
            )
            if f:
                f[0].setCheckState(0, Qt.Checked)


def _event_QCheckTreeWidget(self):
    return self.itemCheckedChanged


# QSlider
def _get_QSlider(self):
    return self.value()


def _set_QSlider(self, v):
    self.setValue(v)


def _event_QSlider(self):
    return self.valueChanged


# QButtonGroup
def _get_QButtonGroup(self):
    return [(nr, btn.isChecked()) for nr, btn in enumerate(self.buttons())]


def _set_QButtonGroup(self, v):
    for idx, state in v:
        self.buttons()[idx].setChecked(state)


def _event_QButtonGroup(self):
    return self.buttonClicked


# QTabWidget
def _get_QTabWidget(self):
    return self.currentIndex()


def _set_QTabWidget(self, v):
    self.setCurrentIndex(v)


def _event_QTabWidget(self):
    return self.currentChanged


HOOKS = {
    QComboBox: (_get_QComboBox, _set_QComboBox, _event_QComboBox),
    QCheckBox: (_get_QCheckBox, _set_QCheckBox, _event_QCheckBox),
    QAction: (_get_QAction, _set_QAction, _event_QAction),
    QActionGroup: (_get_QActionGroup, _set_QActionGroup, _event_QActionGroup),
    QPushButton: (_get_QPushButton, _set_QPushButton, _event_QPushButton),
    QSpinBox: (_get_QSpinBox, _set_QSpinBox, _event_QSpinBox),
    QDoubleSpinBox: (_get_QDoubleSpinBox, _set_QDoubleSpinBox, _event_QDoubleSpinBox),
    QPlainTextEdit: (_get_QPlainTextEdit, _set_QPlainTextEdit, _event_QPlainTextEdit),
    QLineEdit: (_get_QLineEdit, _set_QLineEdit, _event_QLineEdit),
    QListWidget: (_get_QListWidget, _set_QListWidget, _event_QListWidget),
    QSlider: (_get_QSlider, _set_QSlider, _event_QSlider),
    QButtonGroup: (_get_QButtonGroup, _set_QButtonGroup, _event_QButtonGroup),
    QTabWidget: (_get_QTabWidget, _set_QTabWidget, _event_QTabWidget),
}

default_metadata = {
    "prefer_hidden": False,
    "preferred_handler": None,
    "preferred_map_dict": None,
}


class Recalculate(enum.Enum):
    All = enum.auto()
    View = enum.auto()


class ConfigManagerBase(QObject):
    updated = Signal(int)

    def __init__(self, defaults=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mutex = QMutex()
        self.hooks = HOOKS
        self.reset()

        if defaults is None:
            defaults = {}

        # Same mapping as above, used when a config is not set.
        self.defaults = defaults

        self._metadata = {}

    def _get(self, key):
        with QMutexLocker(self.mutex):
            try:
                return self.config[key]
            except KeyError:
                return None

    def _get_default(self, key):
        with QMutexLocker(self.mutex):
            try:
                return self.defaults[key]
            except KeyError:
                return None

    def get(self, key):
        """
        Get a config value for a given key from the config manager.

        Returns the value that matches the given key. If the value is
        not set, a default value will be returned by set_defaults.

        :param key: The configuration key to return a config value for
        :type key: str
        :rtype: Any supported type (str, int, bool, ...)
        """
        v = self._get(key)
        if v is not None:
            return v
        return self._get_default(key)

    def get_metadata(self, key):
        with QMutexLocker(self.mutex):
            try:
                return self._metadata[key]
            except KeyError:
                return default_metadata

    def metadata_as_dict(self):
        """
        Get metadata for all the items.

        If none is set, get_metadata returns the default.
        """
        metadata_dict = {}
        for k, v in self.defaults.items():
            metadata_dict[k] = self.get_metadata(k)

        return metadata_dict

    def set(self, key, value, trigger_handler=True, trigger_update=True):
        """
        Set a config value for a given key in the config manager.

        The optional trigger_update determines whether event hooks will
        trigger for this key and then recalculate. It is useful to
        suppress these when, for example, updating multiple values.

        :param key: The configuration key to set
        :type key: str
        :param value: The value to set the configuration key to
        :type value: Any supported type (str, int, bool, ...)
        :rtype: bool (success)
        """
        old = self._get(key)
        if old is not None and old == value:
            return False  # Not updating

        # Set a value.
        self._set(key, value)

        if trigger_handler and key in self.handlers:
            # Trigger the handler to update the view.
            getter = self.handlers[key].getter
            setter = self.handlers[key].setter

            if setter and getter() != self._get(key):
                setter(self._get(key))

        # Trigger the update notification.
        if trigger_update:
            self.updated.emit(
                self.eventhooks[key]
                if key in self.eventhooks
                else Recalculate.All
            )

        return True

    def set_default(self, key, value, eventhook=Recalculate.All):
        """
        Set the default value for a given key.

        A default value will be returned if the value is not set in the
        current config. It is important to include defaults for all
        possible config values for backwards compatibility with earlier
        versions of a plugin.

        :param key: The configuration key to set
        :type key: str
        :param value: The value to set the configuration key to
        :type value: Any supported type (str, int, bool, ...)
        :param eventhook: Attach either a full recalculation trigger
                          (the default) or a view-only recalculation
                          trigger to these values
        :type eventhook: enum Recalculate.All, Recalculate.View
        """
        self.defaults[key] = value
        self.eventhooks[key] = eventhook
        self.updated.emit(eventhook)

    def set_metadata(self, key, update_dict):
        """
        Set the metadata for a single key.

        :param key: Config item key
        :param update_dict: Dict of changes to the default metadata
        """
        with QMutexLocker(self.mutex):
            m = default_metadata.copy()
            for k, v in update_dict.items():
                if k in default_metadata:
                    m[k] = v
            self._metadata[key] = m

    def set_defaults(self, keyvalues, eventhook=Recalculate.All):
        """
        Set the default value for a set of keys.

        Default values will be returned if a value is not set in the
        current config. It is important to include defaults for all
        possible config values for backwards compatibility with earlier
        versions of a plugin.

        :param keyvalues: A dictionary of keys and values to set as
                          defaults
        :type key: dict
        :param eventhook: Attach either a full recalculation trigger
                          (the default) or a view-only recalculation
                          trigger to these values
        :type eventhook: enum Recalculate.All, Recalculate.View
        """
        for key, value in keyvalues.items():
            self.defaults[key] = value
            self.eventhooks[key] = eventhook

        self.updated.emit(eventhook)

    def replace(self, keyvalues):
        """
        Completely reset the config with a set of key values.

        Note that this does not wipe handlers or triggers (see reset),
        it simply replaces the values in the config entirely. It is
        equivalent of unsetting all keys, followed by a set_many.
        Anything not in the supplied keyvalues will revert to a default.

        :param keyvalues: A dictionary of keys and values to set as
                          defaults
        :type keyvalues: dict
        :param trigger_update: Flag whether to trigger a config update
                               and a recalculation after all the values
                               have been set
        """
        self.config = {}
        self.set_many(keyvalues)

    def set_many(self, keyvalues, trigger_update=True):
        """
        Set the value of multiple config settings simultaneously.

        This postpones triggering of the update signal until all values
        have been set to prevent excess signals. The trigger_update
        option can be set to False to prevent any update at all.

        :param keyvalues: A dictionary of keys and values to set
        :type key: dict
        :param trigger_update: Flag whether to trigger a config update
                               and a recalculation after all the values
                               have been set
        :type trigger_update: bool
        """
        has_updated = False
        for k, v in keyvalues.items():
            u = self.set(k, v, trigger_update=False)
            has_updated = has_updated or u

        if has_updated and trigger_update:
            self.updated.emit(Recalculate.All)

        return has_updated

    def set_many_metadata(self, metadata):
        """
        Set the config manager's metadata attribute. This should be a
        dict with keys matching each config item for which there is
        metadata. The metadata can include a preferred handler, a
        preferred mapper, etc.
        """
        for key, value in metadata.items():
            self.set_metadata(key, value)


    # HANDLERS

    def add_handler(
        self,
        key,
        handler=None,
        mapper=(lambda x: x, lambda x: x),
        default=None,
    ):
        """
        Add a handler (a UI element) for a given config key.

        The supplied handler should be a QWidget or a QAction through
        which the user can change a config setting. An automatic getter,
        setter, and change-event handler is attached which will
        keep the widget and config in sync. The attached handler will
        default to the correct value from the current config.

        An optional mapper may also be provided to handle translation
        from the values shown in the UI and those saved/loaded from the
        config.
        """
        if key in self.handlers:
            # A key is already there, so skip.
            return None

        # If no handler is supplied, we try to create one either by
        # using the preferred_handler item in metadata or by using a
        # default one based on the type.
        if handler is None:
            if self.get_metadata(key)["preferred_handler"] is not None:
                # If there is a preferred handler in the metadata,
                # create one of those. If there is a preferred mapper,
                # then use that.
                handler = self.get_metadata(key)["preferred_handler"]()
                if self.get_metadata(key)["preferred_map_dict"] is not None:
                    mapper = self.get_metadata(key)["preferred_map_dict"]
                    # If we've just created the handler, we need to add
                    # the map dict items.
                    handler.addItems(
                        self.get_metadata(key)["preferred_map_dict"].keys()
                    )
            # There is no preferred handler, so get the default one.
            else:
                handler = self.get_default_handler(type(self.get(key)))
            if handler is None:
                return None

        # Add a mapping handler for converting displayed values to the
        # internal config data.
        if isinstance(mapper, (dict, collections.OrderedDict)):
            # Allow dict types to be used by default.
            mapper = build_dict_mapper(mapper)
        elif isinstance(mapper, list) and isinstance(mapper[0], tuple):
            mapper = build_tuple_mapper(mapper)

        handler._get_map, handler._set_map = mapper

        self.handlers[key] = handler

        # Look for class hooks and add a getter, a setter, and an
        # updater.
        cls = self._get_hook(handler)
        hookg, hooks, hooku = self.hooks[cls]

        handler.getter = _method_type(hookg, handler)
        handler.setter = _method_type(hooks, handler)
        handler.updater = _method_type(hooku, handler)

        logging.debug(f"Add handler {type(handler).__name__} for {key}")
        handler_callback = lambda x=None: self.set(
            key,
            handler.getter(),
            trigger_handler=False
        )
        handler.updater().connect(handler_callback)

        # Store this so we can issue a specific remove on deletes.
        self.handler_callbacks[key] = handler_callback

        # If the key is not in defaults, set the default to match the
        # handler.
        if key not in self.defaults:
            if default is None:
                self.set_default(key, handler.getter())
            else:
                self.set_default(key, default)

        # Keep the handler and the data consistent.
        if self._get(key) is not None:
            handler.setter(self._get(key))

        # If the key is in the defaults, set the handler to the default
        # state, but don't add anything to config.
        elif key in self.defaults:
            handler.setter(self.defaults[key])

    def _get_hook(self, handler):
        fst = lambda x: next(x, None)

        cls = fst(x for x in self.hooks.keys() if x == type(handler))
        if cls is None:
            cls = fst(x for x in self.hooks.keys() if isinstance(handler, x))

        if cls is None:
            raise TypeError(
                f"No handler functions available for this widget type"
                f"{type(handler).__name__}"
            )
        return cls

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
        config = ET.SubElement(root, "Config")
        for ck, cv in list(self.config.items()):
            co = ET.SubElement(config, "ConfigSetting")
            co.set("id", ck)
            t = type(cv).__name__
            co.set("type", type(cv).__name__)
            co = CONVERT_TYPE_TO_XML[t](co, cv)

        return root

    def setXMLConfig(self, root):
        config = {}

        for xconfig in root.findall("Config/ConfigSetting"):
            if xconfig.get("type") in CONVERT_TYPE_FROM_XML:
                v = CONVERT_TYPE_FROM_XML[xconfig.get("type")](xconfig)
            config[xconfig.get("id")] = v

        self.set_many(config, trigger_update=False)

    def as_dict(self):
        """
        Return the combination of defaults and the config being as a
        flat dict (so it can be pickled).
        """
        result_dict = {}
        for k, v in self.defaults.items():
            result_dict[k] = self.get(k)

        return result_dict

    def all_as_dict(self):
        """Return a dict containing defaults, config, and metadata."""
        return {
            "defaults": self.defaults.copy(),
            "config": self.as_dict(),
            "metadata": self.metadata_as_dict(),
        }

    def get_visible_keys(self):
        return [
            k
            for k in self.defaults
            if not self.get_metadata(k)["prefer_hidden"]
        ]

    @staticmethod
    def get_default_handler(in_type):
        """Get the default handler widget based on the input type."""
        if in_type == str:
            return QLineEdit()
        elif in_type == float:
            return QDoubleSpinBox()
        elif in_type == bool:
            return QCheckBox()
        elif in_type == int:
            return QSpinBox()
        else:
            return None


class ConfigManager(ConfigManagerBase):
    default_path = "config.json"

    def __init__(self, *args, filename=None, **kwargs):
        super().__init__(*args, **kwargs)

        if filename is not None:
            self.path = filename
            self.load()
        else:
            self.path = self.default_path

    def reset(self):
        """
        Reset the config manager to its initialised state.

        This clears all values, unsets all defaults, removes all
        handlers, mappings, and hooks.
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
            except KeyError:
                return None

    def _set(self, key, value):
        with QMutexLocker(self.mutex):
            self.config[key] = value

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                self.set_many(json.load(f))

    def save(self):
        pathlib.Path(self.path).parent.mkdir(parents=True, exist_ok=True)

        with open(self.path, "w") as f:
            json.dump(self.as_dict(), f, indent=4)


class QSettingsManager(ConfigManagerBase):

    def __init__(self, *args, warn_no_app_name=True, **kwargs):
        self.warn_no_app_name = warn_no_app_name
        super().__init__(*args, **kwargs)

    def reset(self):
        """
        Reset the config manager to its initialised state.

        This initialises QSettings, unsets all defaults, removes all
        handlers, mappings, and hooks.
        """
        if self.warn_no_app_name:
            app = QApplication.instance()
            if app.applicationName() == "" or app.organizationName() == "":
                warnings.warn(
                    "QApplication.applicationName and QApplication.organizationName "
                    "must be set for QSettings to persist."
                )

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
                # Do an invalidity check for Qt4.
                if type(v) == QVariant and v.type() == QVariant.Invalid:
                    return None

                # Map a type to that in defaults. This is required if a
                # QVariant is a string representation of the actual
                # value (e.g., in the Windows Registry).
                vt = type(v)

                if key in self.defaults:
                    dt = type(self.defaults[key])

                    if vt == QVariant:
                        # The target type is a QVariant, so munge it if
                        # a QVariant is of Qt4.
                        type_munge = {
                            int: v.toInt,
                            float: v.toFloat,
                            str: v.toString,
                            unicode: v.toString,
                            bool: v.toBool,
                            list: v.toStringList,
                        }
                        v = type_munge[dt]()
                    elif vt != dt and vt == basestring:
                        # The value is stored as unicode, so munge it.
                        type_munge = {
                            int: lambda x: int(x),
                            float: lambda x: float(x),
                            str: lambda x: str(x),
                            bool: lambda x: x.lower() == u"true",
                        }
                        v = type_munge[dt](v)

                    v = dt(v)

                return v
            else:
                return None

    def _set(self, key, value):
        with QMutexLocker(self.mutex):
            self.settings.setValue(key, value)


class ConfigDialog(QtWidgets.QDialog):
    """
    Create a layout from the input config using build_config_layout and
    a QDialogButtonBox with OK and Cancel buttons.
    """

    def __init__(self, config, *args, cols=None, **kwargs):
        if "PyQt5" in sys.modules:
            f = kwargs.pop("f", None)

            if f is not None:
                kwargs["flags"] = f
        elif "PySide2" in sys.modules:
            flags = kwargs.pop("flags", None)
            if flags is not None:
                kwargs["f"] = flags

        super().__init__(*args, **kwargs)
        config_dict = config.all_as_dict()
        self.config = ConfigManager(config_dict["defaults"])
        self.config.set_many(config_dict["config"])
        self.config.set_many_metadata(config_dict["metadata"])

        # Build a layout from the settings.
        config_layout_kwargs = {} if cols is None else {"cols": cols}
        config_layout = build_config_layout(self.config, **config_layout_kwargs)

        # Create a button box for the dialog.
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Reset
            | QtWidgets.QDialogButtonBox.Ok
            | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # The QDialogButtonBox places Reset after OK and Cancel.
        button_box.buttons()[2].setText("Reset to Defaults")
        button_box.buttons()[2].clicked.connect(self.show_confirm_reset_dialog)

        # Place everything in a layout in the dialog.
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(config_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def show_confirm_reset_dialog(self):
        message_box = QtWidgets.QMessageBox(
            self,
            text="Are you sure you want to reset to defaults?"
        )
        message_box.setWindowTitle("Warning")
        message_box.setStandardButtons(
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
        )
        message_box.buttonClicked.connect(
            lambda button: (
                self.config.set_many(self.config.defaults)
                if button.text() == "OK"
                else None
            )
        )
        message_box.exec()


def build_config_layout(config, cols=2):
    """
    Generate a layout based on the input of the ConfigManager.

    The layout consists of a user-specified number of columns of a
    QFormLayout. In each row of the QFormLayout, the label is the config
    dict key, and the field is the config handler for that key.

    :param config: ConfigManager instance
    :param cols: Number of columns to use (default is 2)
    :return: QHBoxLayout
    """
    h_layout = QtWidgets.QHBoxLayout()
    forms = [QtWidgets.QFormLayout() for _ in range(cols)]

    for form in forms:
        h_layout.addLayout(form)

    num_items = len(config.get_visible_keys())

    for i, key in enumerate(config.get_visible_keys()):
        # Find which column to put the setting in. Columns are filled
        # equally, with the remainder to the left. Each column is filled
        # before proceeding to the next one.
        f_index = 0

        for j in range(cols):
            if (i + 1) <= math.ceil((j + 1) * num_items / cols):
                f_index = j
                break

        # Get the handler widget for the key.
        if key in config.handlers:
            # If we've already defined a handler, use that.
            input_widget = config.handlers[key]
        else:
            # Otherwise, try to add a handler. If the handler fails,
            # skip this row.
            config.add_handler(key)

            if key not in config.handlers:
                continue
            else:
                input_widget = config.handlers[key]

        label = QtWidgets.QLabel(key)
        forms[f_index].addRow(label, input_widget)

    return h_layout

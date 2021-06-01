import PyQt5
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from math import ceil
from pyqtconfig import ConfigManager

default_settings = {
    "Setting 1": "Hello",
    "Setting 2": 25,
    "Setting 3": 12.5,
    "Setting 4": False,
}

default_settings_metadata = {
    "Setting 2": {
        "preferred_handler": QtWidgets.QComboBox,
        "preferred_map_dict": {
            "Choice A": 25,
            "Choice B": 26,
            "Choice C": 27
        }
    },
    "Setting 3": {
        "prefer_hidden": True
    }
}


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        self.layout = QtWidgets.QVBoxLayout(self._main)

        self.current_config = QtWidgets.QTextEdit()
        self.settings_button = QtWidgets.QPushButton("Settings")
        self.layout.addWidget(self.current_config)
        self.layout.addWidget(self.settings_button)

        self.config = ConfigManager(default_settings)
        self.config.set_metadata(default_settings_metadata)
        self.config.updated.connect(self.show_config)
        self.show_config()

        self.settings_button.clicked.connect(self.create_config_dialog)

    def create_config_dialog(self):
        config_copy = ConfigManager(self.config.as_dict())
        config_copy.set_metadata(self.config.metadata)
        config_dialog = ConfigDialog(config_copy, self, cols=2, flags=Qt.WindowCloseButtonHint)
        config_dialog.setWindowTitle("Settings")
        config_dialog.setMaximumWidth(100)
        config_dialog.accepted.connect(lambda: self.update_config(config_dialog.config))
        config_dialog.exec()

    def update_config(self, update):
        self.config.set_many(update.as_dict())

    def show_config(self):
        self.current_config.setText(str(self.config.as_dict()))


class ConfigDialog(QtWidgets.QDialog):
    """
    A Dialog class inheriting from QtWidgets.QDialog. This class creates layout from the input config using
    build_config_layout, as well as QDialogButtonBox with Ok and Cancel buttons.
    """
    def __init__(self, config, *args, cols=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config

        # Build layout from settings
        config_layout_kwargs = {} if cols is None else {"cols": cols}
        config_layout = build_config_layout(config, **config_layout_kwargs)

        # Create a button box for the dialog
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Place everything in a layout in the dialog
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(config_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)


def build_config_layout(config, cols=2):
    """
    Generate a layout based on the input ConfigManager. The layout consists of a user specified number of columns of
    QFormLayout. In each row of the QFormLayout, the label is the config dict key, and the field is the config handler
    for that key.

    :param config: ConfigManager
    :param cols: Number of columns to use
    :return: QHBoxLayout
    """
    h_layout = QtWidgets.QHBoxLayout()
    forms = [QtWidgets.QFormLayout() for _ in range(cols)]
    for form in forms:
        h_layout.addLayout(form)

    num_prefer_hidden = 0
    for k, v in config.metadata.items():
        if "prefer_hidden" in v:
            if v["prefer_hidden"]:
                num_prefer_hidden += 1

    num_items = len(config.as_dict()) - num_prefer_hidden

    i = -1
    for key in config.as_dict():
        if key in config.metadata and "prefer_hidden" in config.metadata[key]:
            # If the key doesn't want to be shown, skip this row
            if config.metadata[key]["prefer_hidden"]:
                continue

        i += 1

        # Find which column to put the setting in. Columns are filled equally, with remainder to the left. Each column
        # is filled before proceeding to the next.
        f_index = 0
        for j in range(cols):
            if (i+1) <= ceil((j+1)*num_items/cols):
                f_index = j
                break

        # Get the handler widget for the key
        if key in config.handlers:
            # If we've already defined a handler, use that
            input_widget = config.handlers[key]
        elif key in config.metadata and "preferred_handler" in config.metadata[key]:
            # If there is a preferred handler in the metadata, create one of those. If there is a preferred mapper
            # use that
            input_widget = config.metadata[key]["preferred_handler"]()
            if "preferred_map_dict" in config.metadata[key]:
                input_widget.addItems(config.metadata[key]["preferred_map_dict"].keys())
                config.add_handler(key, input_widget, mapper=config.metadata[key]["preferred_map_dict"])
            else:
                config.add_handler(key, input_widget)
        else:
            # If there's no existing handler or preferred handler, try to create a default one. If it fails, skip this
            # row
            config.add_handler(key)
            if key not in config.handlers:
                continue
            else:
                input_widget = config.handlers[key]

        label = QtWidgets.QLabel(key)
        forms[f_index].addRow(label, input_widget)

    return h_layout


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    main_window = MainWindow()
    main_window.setWindowTitle("Settings Dialog Demo")
    main_window.setMinimumSize(300, 250)
    main_window.show()

    app.exec()

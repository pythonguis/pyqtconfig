import PyQt5
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from pyqtconfig import ConfigManager, ConfigDialog

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

        self.config = ConfigManager(default_settings, load_file=True, filename="config/settings_config.json")
        self.config.set_many_metadata(default_settings_metadata)
        self.config.updated.connect(self.show_config)
        self.show_config()

        self.settings_button.clicked.connect(self.create_config_dialog)

    def create_config_dialog(self):
        config_dialog = ConfigDialog(self.config, self, cols=2, f=Qt.WindowCloseButtonHint)
        config_dialog.setWindowTitle("Settings")
        config_dialog.setMaximumWidth(100)
        config_dialog.accepted.connect(lambda: self.update_config(config_dialog.config))
        config_dialog.exec()

    def update_config(self, update):
        self.config.set_many(update.as_dict())
        self.config.save()

    def show_config(self):
        self.current_config.setText(str(self.config.as_dict()))


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    main_window = MainWindow()
    main_window.setWindowTitle("Settings Dialog Demo")
    main_window.setMinimumSize(300, 250)
    main_window.show()

    app.exec_()

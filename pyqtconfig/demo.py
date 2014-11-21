from .qt import *
from pyqtconfig import ConfigManager

    
class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle('PyQtConfig Demo')
        self.config = ConfigManager()

        CHOICE_A = 1
        CHOICE_B = 2
        CHOICE_C = 3
        CHOICE_D = 4

        map_dict = {
            'Choice A': CHOICE_A,
            'Choice B': CHOICE_B,
            'Choice C': CHOICE_C,
            'Choice D': CHOICE_D,
        }

        self.config.set_defaults({
            'number': 13,
            'text': 'hello',
            'active': True,
            'combo': CHOICE_C,
        })

        gd = QGridLayout()

        sb = QSpinBox()
        gd.addWidget(sb, 0, 1)
        self.config.add_handler('number', sb)

        te = QLineEdit()
        gd.addWidget(te, 1, 1)
        self.config.add_handler('text', te)

        cb = QCheckBox()
        gd.addWidget(cb, 2, 1)
        self.config.add_handler('active', cb)

        cmb = QComboBox()
        cmb.addItems(map_dict.keys())
        gd.addWidget(cmb, 3, 1)
        self.config.add_handler('combo', cmb, mapper=map_dict)

        self.current_config_output = QTextEdit()
        gd.addWidget(self.current_config_output, 0, 3, 3, 1)

        self.config.updated.connect(self.show_config)

        self.show_config()

        self.window = QWidget()
        self.window.setLayout(gd)
        self.setCentralWidget(self.window)

    def show_config(self):
        self.current_config_output.setText(str(self.config.as_dict()))

# Create a Qt application
app = QApplication(sys.argv)
app.setOrganizationName("PyQtConfig")
app.setOrganizationDomain("martinfitzpatrick.name")
app.setApplicationName("PyQtConfig")

w = MainWindow()
w.show()
app.exec_()  # Enter Qt application main loop

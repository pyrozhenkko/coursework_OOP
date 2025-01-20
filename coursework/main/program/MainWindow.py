from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
from LoginWindow import LoginWindow
from RegisterChoiceWindow import RegisterChoiceWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login or Register")
        self.initUI()

    def initUI(self):
        self.resize(800, 600)
        self.setFixedSize(800, 600)

        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(0, 42, 85))
        self.setPalette(palette)

        layout = QVBoxLayout()

        self.login_button = QPushButton("Login")
        self.register_button = QPushButton("Register")

        button_style = """
        QPushButton {
            font-size: 20px;
            color: white;
            background-color: #3498db; 
            padding: 15px;
            border: 2px;
            border-radius: 12px;
            border: none;
            transition: background-color 1s ease, transform 1s ease;
            width: 250px;
            margin: 15px;
        }
        QPushButton:hover {
            background-color: #2980b9;
            transition: 1s;
            transform: scale(1.05);
        }
        QPushButton:pressed {
            background-color: #1f6b97;
            transform: scale(0.98);
        }
        """

        self.login_button.setStyleSheet(button_style)
        self.register_button.setStyleSheet(button_style)

        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        layout.setAlignment(Qt.AlignCenter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def login(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def register(self):
        self.register_choice_window = RegisterChoiceWindow()
        self.register_choice_window.show()
        self.close()

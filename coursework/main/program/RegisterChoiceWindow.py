from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QWidget
from StudentRegisterWindow import StudentRegisterWindow
from main.program.TeacherRegisterWindow import TeacherRegisterWindow


class RegisterChoiceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.student_button = QPushButton("Register as Student")
        self.teacher_button = QPushButton("Register as Teacher")

        button_style = """
        QPushButton {
            font-size: 18px;
            color: white;
            background-color: #3498db;
            padding: 12px;
            border: none;
            border-radius: 12px;
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

        self.student_button.setStyleSheet(button_style)
        self.teacher_button.setStyleSheet(button_style)

        self.student_button.clicked.connect(self.register_student)
        self.teacher_button.clicked.connect(self.register_teacher)

        layout.addWidget(self.student_button)
        layout.addWidget(self.teacher_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def register_student(self):
        self.student_register_window = StudentRegisterWindow()
        self.student_register_window.show()
        self.close()

    def register_teacher(self):
        self.teacher_register_window = TeacherRegisterWindow()
        self.teacher_register_window.show()
        self.close()

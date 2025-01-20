from PyQt5.QtCore import Qt
from StudentWindow import StudentWindow
from TeacherWindow import TeacherWindow
from PyQt5.QtWidgets import (QRadioButton, QLineEdit)
from werkzeug.security import check_password_hash
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel, QMessageBox, QWidget, QMainWindow
import pyodbc
from main.program import connection_string


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 200)

        self.label_login = QLabel("Full name:")
        self.input_login = QLineEdit()

        self.label_password = QLabel("Password:")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)

        self.radio_student = QRadioButton("Student")
        self.radio_teacher = QRadioButton("Teacher")

        self.login_button = QPushButton("Enter")
        self.login_button.clicked.connect(self.handle_login)

        label_style = """
        QLabel {
            font-size: 14px;
            color: black; 
        }
        """

        input_style = """
        QLineEdit {
            font-size: 16px;
            padding: 10px;
            background-color: #ffffff;
            border-radius: 8px;
            border: 2px solid #3498db;
        }
        QLineEdit:focus {
            border-color: #2980b9;
        }
        """

        radio_button_style = """
        QRadioButton {
            font-size: 16px;
            color: black;  
        }
        QRadioButton::indicator {
            border: 2px solid #3498db;
            border-radius: 10px;
        }
        QRadioButton::indicator:checked {
            background-color: #3498db;
        }
        """

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

        self.setStyleSheet(label_style)
        self.input_login.setStyleSheet(input_style)
        self.input_password.setStyleSheet(input_style)
        self.radio_student.setStyleSheet(radio_button_style)
        self.radio_teacher.setStyleSheet(radio_button_style)
        self.login_button.setStyleSheet(button_style)

        layout = QVBoxLayout()
        layout.addWidget(self.label_login)
        layout.addWidget(self.input_login)
        layout.addWidget(self.label_password)
        layout.addWidget(self.input_password)
        layout.addWidget(self.radio_student)
        layout.addWidget(self.radio_teacher)
        layout.addWidget(self.login_button)

        layout.setAlignment(Qt.AlignCenter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def handle_login(self):
        login = self.input_login.text()
        password = self.input_password.text()

        if not login or not password:
            QMessageBox.warning(self, "Error", "Invalid login or password.")
            return

        if not (self.radio_student.isChecked() or self.radio_teacher.isChecked()):
            QMessageBox.warning(self, "Error", "Choose a role.")
            return

        try:
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()

            if self.radio_teacher.isChecked():
                cursor.execute("SELECT teacher_id, password FROM Teachers WHERE login = ?", (login,))
                teacher = cursor.fetchone()
                if teacher and check_password_hash(teacher[1], password):
                    self.open_teacher_window(teacher[0])
                    return

            elif self.radio_student.isChecked():
                cursor.execute("SELECT student_id, password FROM Students WHERE login = ?", (login,))
                student = cursor.fetchone()
                if student and check_password_hash(student[1], password):
                    self.open_student_window(student[0])
                    return

            QMessageBox.warning(self, "Error", "Invalid login or password.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"DatabaseError: {str(e)}")

    def open_teacher_window(self, teacher_id):
        self.teacher_window = TeacherWindow(teacher_id)
        self.teacher_window.show()
        self.close()

    def open_student_window(self, student_id):
        self.student_window = StudentWindow(student_id)
        self.student_window.show()
        self.close()



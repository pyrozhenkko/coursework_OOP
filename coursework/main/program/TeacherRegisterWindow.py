import pyodbc
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QMessageBox, QComboBox)
from werkzeug.security import generate_password_hash
from main.program import connection_string


class TeacherRegisterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def load_subjects(self):
        try:
            with pyodbc.connect(connection_string) as conn:
                cursor = conn.cursor()

                query = "SELECT subject_name FROM Subjects"
                cursor.execute(query)

                subjects = cursor.fetchall()

                sorted_subjects = sorted([subject[0] for subject in subjects])

                sorted_subjects.insert(0, "None")

                self.subject_combobox.clear()

                for subject_name in sorted_subjects:
                    self.subject_combobox.addItem(subject_name)
        except pyodbc.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load subjects: {str(e)}")

    def register_teacher(self):
        login = self.login_input.text()
        password = self.password_input.text()
        subject_name = self.subject_combobox.currentText()

        if not login or not password:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        if subject_name == "None" and not self.new_subject_input.text():
            QMessageBox.warning(self, "Subject Error", "Please select a subject or enter a new one.")
            return

        if subject_name == "None":
            subject_name = self.new_subject_input.text().strip()

        if not subject_name:
            QMessageBox.warning(self, "Subject Error", "Please enter a subject name.")
            return

        try:
            if subject_name != "None":
                with pyodbc.connect(connection_string) as conn:
                    cursor = conn.cursor()
                    query = "SELECT COUNT(*) FROM Subjects WHERE subject_name = ?"
                    cursor.execute(query, (subject_name,))
                    count = cursor.fetchone()[0]

                    if count == 0:
                        query = "INSERT INTO Subjects (subject_name) VALUES (?)"
                        cursor.execute(query, (subject_name,))
                        conn.commit()
                        QMessageBox.information(self, "Success", f"Subject '{subject_name}' added successfully.")

            hashed_password = generate_password_hash(password)

            with pyodbc.connect(connection_string) as conn:
                cursor = conn.cursor()

                query = "INSERT INTO Teachers (login, password, subject_name) VALUES (?, ?, ?)"
                cursor.execute(query, (login, hashed_password, subject_name))

                conn.commit()
                QMessageBox.information(self, "Success", "Teacher registered successfully.")
        except pyodbc.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to register teacher: {str(e)}")

    def initUI(self):
        layout = QVBoxLayout()

        self.login_label = QLabel("Login:")
        self.login_input = QLineEdit()

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.subject_label = QLabel("Subject name:")
        self.subject_combobox = QComboBox()

        self.new_subject_label = QLabel("New subject (if any):")
        self.new_subject_input = QLineEdit()

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.register_teacher)

        layout.addWidget(self.login_label)
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.subject_label)
        layout.addWidget(self.subject_combobox)
        layout.addWidget(self.new_subject_label)
        layout.addWidget(self.new_subject_input)
        layout.addWidget(self.submit_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_subjects()

        label_style = """
           QLabel {
               font-size: 16px;
               color: black;
           }
           """
        input_style = """
           QLineEdit {
               font-size: 16px;
               padding: 8px;
               border-radius: 8px;
               border: 2px solid #3498db;
           }
           """
        combobox_style = """
           QComboBox {
               font-size: 16px;
               padding: 8px;
               border-radius: 8px;
               border: 2px solid #3498db;
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

        self.login_label.setStyleSheet(label_style)
        self.password_label.setStyleSheet(label_style)
        self.subject_label.setStyleSheet(label_style)
        self.new_subject_label.setStyleSheet(label_style)

        self.login_input.setStyleSheet(input_style)
        self.password_input.setStyleSheet(input_style)
        self.subject_combobox.setStyleSheet(combobox_style)
        self.new_subject_input.setStyleSheet(input_style)
        self.submit_button.setStyleSheet(button_style)

        self.setGeometry(500, 300, 400, 300)
        self.setFixedSize(500, 500)
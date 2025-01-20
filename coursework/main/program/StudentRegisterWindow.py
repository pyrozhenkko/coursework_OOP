import pyodbc
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QWidget, QComboBox
)
from werkzeug.security import generate_password_hash
from main.program import connection_string

class StudentRegisterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register as Student")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.login_label = QLabel("Login:")
        self.login_input = QLineEdit()

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.class_label = QLabel("Class name:")
        self.class_combobox = QComboBox()

        self.new_class_label = QLabel("New class (if any):")
        self.new_class_input = QLineEdit()

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.register_student)

        layout.addWidget(self.login_label)
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.class_label)
        layout.addWidget(self.class_combobox)
        layout.addWidget(self.new_class_label)
        layout.addWidget(self.new_class_input)
        layout.addWidget(self.submit_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_classes()

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
        self.class_label.setStyleSheet(label_style)
        self.new_class_label.setStyleSheet(label_style)

        self.login_input.setStyleSheet(input_style)
        self.password_input.setStyleSheet(input_style)
        self.class_combobox.setStyleSheet(combobox_style)
        self.new_class_input.setStyleSheet(input_style)
        self.submit_button.setStyleSheet(button_style)

        self.setGeometry(500, 300, 400, 300)
        self.setFixedSize(500, 400)

    def load_classes(self):
        try:
            with pyodbc.connect(connection_string) as conn:
                cursor = conn.cursor()

                query = "SELECT class_name FROM Classes"
                cursor.execute(query)

                classes = cursor.fetchall()

                sorted_classes = sorted([class_row[0] for class_row in classes])

                sorted_classes.insert(0, "None")

                self.class_combobox.clear()
                for class_name in sorted_classes:
                    self.class_combobox.addItem(class_name)
        except pyodbc.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load classes: {str(e)}")

    def register_student(self):
        login = self.login_input.text()
        password = self.password_input.text()
        class_name = self.class_combobox.currentText()

        if not login or not password:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        if class_name == "None" and not self.new_class_input.text():
            QMessageBox.warning(self, "Class Error", "Please select a class or enter a new one.")
            return

        if class_name == "None":
            class_name = self.new_class_input.text().strip()

        if not class_name:
            QMessageBox.warning(self, "Class Error", "Please enter a class name.")
            return

        try:
            if class_name != "None":
                with pyodbc.connect(connection_string) as conn:
                    cursor = conn.cursor()
                    query = "SELECT COUNT(*) FROM Classes WHERE class_name = ?"
                    cursor.execute(query, (class_name,))
                    count = cursor.fetchone()[0]

                    if count == 0:
                        query = "INSERT INTO Classes (class_name) VALUES (?)"
                        cursor.execute(query, (class_name,))
                        conn.commit()
                        QMessageBox.information(self, "Success", f"Class '{class_name}' added successfully.")

            hashed_password = generate_password_hash(password)

            with pyodbc.connect(connection_string) as conn:
                cursor = conn.cursor()

                query = "INSERT INTO Students (login, password, class_name) VALUES (?, ?, ?)"
                cursor.execute(query, (login, hashed_password, class_name))

                conn.commit()
                QMessageBox.information(self, "Success", "Student registered successfully.")
        except pyodbc.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to register student: {str(e)}")

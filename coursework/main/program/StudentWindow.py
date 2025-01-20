from datetime import datetime
import pyodbc
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDateEdit, QMessageBox, \
    QTableWidgetItem, QTableWidget, QHeaderView, QPushButton
from main.program import connection_string

connection_string = (
    "DRIVER={SQL Server};"
    "SERVER=SPACECRAB\MSSQLSERVER01;" 
    "DATABASE=SchoolDB2;"
)

class Node:
    def __init__(self, data=None):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        last_node = self.head
        while last_node.next:
            last_node = last_node.next
        last_node.next = new_node

    def get_all(self):
        current = self.head
        result = []
        while current:
            result.append(current.data)
            current = current.next
        return result

class StudentWindow(QMainWindow):
    def __init__(self, student_id):
        super().__init__()
        self.grades_data = LinkedList()
        self.student_id = student_id
        self.subject_list = LinkedList()
        self.student_name = ""
        self.class_name = ""
        self.grades_data = LinkedList()
        self.init_student_info()
        self.setWindowTitle(f"Journal - {self.student_name}")
        self.showMaximized()

        main_widget = QWidget()
        layout = QVBoxLayout()

        info_layout = QHBoxLayout()
        self.student_info_label = QLabel(f"Student: {self.student_name} | Class: {self.class_name}")
        info_layout.addWidget(self.student_info_label)
        info_layout.addStretch()

        filter_layout = QHBoxLayout()
        self.subject_combo = QComboBox()
        self.subject_combo.addItem("ALl subjects")

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())

        filter_layout.addWidget(QLabel("Subject:"))
        filter_layout.addWidget(self.subject_combo)
        filter_layout.addWidget(QLabel("Since:"))
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(QLabel("to:"))
        filter_layout.addWidget(self.date_to)
        filter_layout.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Subject", "Assignment", "Description", "Mark"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.refresh_button = QPushButton("Update")

        layout.addLayout(info_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(self.table)
        layout.addWidget(self.refresh_button)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        self.refresh_button.clicked.connect(self.load_grades)
        self.subject_combo.currentTextChanged.connect(self.load_grades)
        self.date_from.dateChanged.connect(self.load_grades)
        self.date_to.dateChanged.connect(self.load_grades)

        self.load_subjects()
        self.load_grades()
        self.table.setSortingEnabled(True)

    def update_table_with_grades(self, grades):
        self.table.setRowCount(len(grades))
        for row, (date, subject, task, desc, grade) in enumerate(grades):
            # Date
            if isinstance(date, str):
                try:
                    date = datetime.strptime(date, "%Y-%m-%d").date()
                except ValueError:
                    pass

            date_item = QTableWidgetItem(date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date))
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, date_item)

            # Subject
            subject_item = QTableWidgetItem(subject)
            subject_item.setFlags(subject_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, subject_item)

            # Task
            task_item = QTableWidgetItem(task)
            task_item.setFlags(task_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, task_item)

            # Description
            desc_item = QTableWidgetItem(desc if desc else "-")
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, desc_item)

            # Grade
            grade_item = QTableWidgetItem(str(grade) if grade else "-")
            grade_item.setFlags(grade_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 4, grade_item)

        self.table.sortItems(0, Qt.AscendingOrder)

    def init_student_info(self):
        try:
            with pyodbc.connect(connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute(""" 
                    SELECT login, class_name 
                    FROM Students 
                    WHERE student_id = ? 
                """, self.student_id)
                result = cursor.fetchone()
                if result:
                    self.student_name = result[0]
                    self.class_name = result[1]
                else:
                    raise Exception("Student isn`t found")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error getting information about the student: {str(e)}")
            self.close()

    def get_database_connection(self):
        try:
            return pyodbc.connect(connection_string)
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to database: {str(e)}")
            return None

    def load_subjects(self):
        conn = self.get_database_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute(""" 
                SELECT DISTINCT subject_name 
                FROM TeacherInterface 
                WHERE student_login = (SELECT login FROM Students WHERE student_id = ?) 
                ORDER BY subject_name
            """, self.student_id)

            # Створення однозв'язного списку для зберігання предметів
            subjects_list = LinkedList()
            subjects_list.append("All subjects")  # Додаємо "All subjects" як перший елемент списку

            for subject in cursor.fetchall():
                subjects_list.append(subject[0])  # Додаємо кожен предмет до списку

            # Оновлення комбобоксу з використанням даних з однозв'язного списку
            self.subject_combo.clear()
            self.subject_combo.addItems(subjects_list.get_all())

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading items: {str(e)}")
        finally:
            conn.close()

    def load_grades(self):
        conn = self.get_database_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()

            base_query = """
                SELECT 
                    date,
                    subject_name,
                    task_name,
                    task_description,
                    grade
                FROM TeacherInterface
                WHERE student_login = (SELECT login FROM Students WHERE student_id = ?)
                AND CAST(date AS DATE) BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
            """

            params = [
                self.student_id,
                self.date_from.date().toString("yyyy-MM-dd"),
                self.date_to.date().toString("yyyy-MM-dd")
            ]

            if self.subject_combo.currentText() != "All subjects":
                base_query += " AND subject_name = ?"
                params.append(self.subject_combo.currentText())

            base_query += " ORDER BY date DESC, subject_name"

            cursor.execute(base_query, params)
            grades = cursor.fetchall()

            grades_list = []
            for grade in grades:
                grades_list.append(grade)

            self.update_table_with_grades(grades_list)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading grades: {str(e)}")
        finally:
            conn.close()
    def update_table_with_grades(self, grades):
        self.table.setRowCount(len(grades))
        for row, (date, subject, task, desc, grade) in enumerate(grades):
            # Date
            if isinstance(date, str):
                try:
                    date = datetime.strptime(date, "%Y-%m-%d").date()
                except ValueError:
                    pass

            date_item = QTableWidgetItem(date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date))
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, date_item)

            # Subject
            subject_item = QTableWidgetItem(subject)
            subject_item.setFlags(subject_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, subject_item)

            task_item = QTableWidgetItem(task)
            task_item.setFlags(task_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, task_item)

            # Description
            desc_item = QTableWidgetItem(desc if desc else "-")
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, desc_item)

            # Grade
            grade_item = QTableWidgetItem(str(grade) if grade else "-")
            grade_item.setFlags(grade_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 4, grade_item)
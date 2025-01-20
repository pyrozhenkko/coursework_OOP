from datetime import datetime
import Extension

import pyodbc
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton, QDateEdit, \
    QTableWidget, QMessageBox, QInputDialog, QTableWidgetItem, QHeaderView, QDialog, QFormLayout, QLineEdit
from werkzeug.security import generate_password_hash

from main.program import connection_string

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


    def delete(self, data):
        current = self.head
        prev = None

        if current and current.data == data:
            self.head = current.next
            current = None
            return

        while current and current.data != data:
            prev = current
            current = current.next

        if current is None:
            return

        prev.next = current.next
        current = None

class TeacherWindow(QMainWindow):
    def __init__(self, teacher_id):
        super().__init__()
        self.teacher_id = teacher_id
        self.students_list = LinkedList()
        self.tasks_list = LinkedList()
        self.setWindowTitle("School journal")
        self.showMaximized()

        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT subject_name FROM Teachers WHERE teacher_id = ?", (self.teacher_id,))
        subject_row = cursor.fetchone()
        self.subject_name = subject_row[0] if subject_row else None
        conn.close()

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        self.subject_label = QLabel(f"Subject: {self.subject_name}")
        self.subject_label.setStyleSheet("font-weight: bold;")

        top_panel = QHBoxLayout()
        self.top_panel = top_panel
        top_panel.addWidget(self.subject_label)
        self.class_label = QLabel("Class:")
        self.class_combo = QComboBox()
        self.select_button = QPushButton("Show")
        self.add_task_button = QPushButton("Add an assignment")
        self.delete_task_button = QPushButton("Delete an assignment")
        self.add_student_button = QPushButton("Add a student")
        self.delete_student_button = QPushButton("Delete a student")
        self.date_label = QLabel("Date of the assignment:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        self.search_label = QLabel("Find a student:")
        self.search_input = QLineEdit()
        self.search_button = QPushButton("Find")

        top_panel.addWidget(self.class_label)
        top_panel.addWidget(self.class_combo)
        top_panel.addWidget(self.date_label)
        top_panel.addWidget(self.date_edit)
        top_panel.addWidget(self.select_button)
        top_panel.addWidget(self.add_task_button)
        top_panel.addWidget(self.delete_task_button)
        top_panel.addWidget(self.add_student_button)
        top_panel.addWidget(self.delete_student_button)
        top_panel.addWidget(self.search_label)
        top_panel.addWidget(self.search_input)
        top_panel.addWidget(self.search_button)
        top_panel.addStretch()

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.DoubleClicked)
        self.table.setSortingEnabled(True)

        self.save_button = QPushButton("Save")

        main_layout.addLayout(top_panel)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.save_button)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.select_button.clicked.connect(self.load_class_data)
        self.save_button.clicked.connect(self.save_changes)
        self.add_task_button.clicked.connect(self.add_new_task)
        self.delete_task_button.clicked.connect(self.delete_task)
        self.search_button.clicked.connect(self.search_student)
        self.add_student_button.clicked.connect(self.add_student)
        self.delete_student_button.clicked.connect(self.delete_student)

        self.load_classes()

    def add_student(self):
        class_name = self.class_combo.currentText()
        if not class_name:
            QMessageBox.warning(self, "Warning", "Select a class first")
            return

        student_login, ok = QInputDialog.getText(self, "Adding student", "Enter student login:")
        if ok and student_login:
            try:
                conn = pyodbc.connect(connection_string)
                cursor = conn.cursor()

                cursor.execute("SELECT 1 FROM Students WHERE login = ? AND class_name = ?", (student_login, class_name))
                if cursor.fetchone():
                    QMessageBox.warning(self, "Warning", f"Student already exists in class {class_name}.")
                    return

                student_password, ok = QInputDialog.getText(self, "Adding password", "Enter student password:")
                if not ok or not student_password:
                    QMessageBox.warning(self, "Warning", "Password cannot be empty.")
                    return

                hashed_password = generate_password_hash(student_password)

                # Add to linked list first
                student_data = {"login": student_login, "class": class_name, "password": hashed_password}
                self.students_list.append(student_data)

                # Then add to database
                cursor.execute("""
                    INSERT INTO Students (login, password, class_name) 
                    VALUES (?, ?, ?)
                """, (student_login, hashed_password, class_name))

                conn.commit()
                QMessageBox.information(self, "Success", "Student added successfully.")
                self.load_class_data()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error adding student: {str(e)}")
            finally:
                conn.close()

    def delete_student(self):
        class_name = self.class_combo.currentText()
        if not class_name:
            QMessageBox.warning(self, "Warning", "Select a class first")
            return

        student_login, ok = QInputDialog.getText(self, "Student deletion", "Enter student login:")
        if ok and student_login:
            try:
                # Delete from linked list first
                student_data = {"login": student_login, "class": class_name}
                self.students_list.delete(student_data)

                # Then delete from database
                conn = pyodbc.connect(connection_string)
                cursor = conn.cursor()
                cursor.execute("""
                       DELETE FROM Students 
                       WHERE login = ? AND class_name = ?
                   """, (student_login, class_name))

                if cursor.rowcount == 0:
                    QMessageBox.warning(self, "Warning", "Student not found.")
                    return

                conn.commit()
                QMessageBox.information(self, "Success", "Student deleted successfully.")
                self.load_class_data()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error deleting student: {str(e)}")
            finally:
                conn.close()
    def search_student(self):
            student_login = self.search_input.text().strip()

            if not student_login:
                for row in range(self.table.rowCount()):
                    self.table.showRow(row)
                QMessageBox.warning(self, "Warning", "Enter student login to search.")
                return

            student_logins = []
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 1)
                if item and item.text():
                    student_logins.append(item.text())

            if not student_logins:
                QMessageBox.warning(self, "Warning", "List of students is empty")
                return

            Extension.quickSort(student_logins, 0, len(student_logins) - 1)

            index = Extension.binarySearch(student_logins, student_login)

            if index != -1:
                for row in range(self.table.rowCount()):
                    self.table.hideRow(row)

                for row in range(self.table.rowCount()):
                    current_login = self.table.item(row, 1)
                    if current_login and current_login.text() == student_login:
                        self.table.showRow(row)
                        self.table.selectRow(row)
                        self.add_reset_button()
                        return
            else:
                for row in range(self.table.rowCount()):
                    self.table.showRow(row)
                QMessageBox.warning(self, "Search result", "Student not found.")

    def add_reset_button(self):
        if not hasattr(self, 'reset_search_button'):
            self.reset_search_button = QPushButton("Show all")
            self.reset_search_button.clicked.connect(self.reset_search)
            for i in range(self.top_panel.count()):
                if self.top_panel.itemAt(i).widget() == self.search_button:
                    self.top_panel.insertWidget(i + 1, self.reset_search_button)
                    break

    def reset_search(self):
        self.search_input.clear()
        for row in range(self.table.rowCount()):
            self.table.showRow(row)
        if hasattr(self, 'reset_search_button'):
            self.reset_search_button.hide()

    def load_classes(self):
        try:
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT class_name FROM Students ORDER BY class_name")
            classes = cursor.fetchall()

            self.class_combo.clear()

            for class_name in classes:
                self.class_combo.addItem(str(class_name[0]))

            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading class list: {str(e)}")


    def save_changes(self):
        try:
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()

            class_name = self.class_combo.currentText()
            current_date = self.date_edit.date().toString("yyyy-MM-dd")

            cursor.execute("SELECT subject_name FROM Teachers WHERE teacher_id = ?", (self.teacher_id,))
            subject_row = cursor.fetchone()

            if not subject_row:
                QMessageBox.critical(self, "Error", "Failed to find the subject for the teacher.")
                return

            subject_name = subject_row[0]

            for row in range(self.table.rowCount()):
                student_login_item = self.table.item(row, 1)
                if student_login_item is None or student_login_item.text() is None:
                    continue

                student_login = student_login_item.text()

                for col in range(2, self.table.columnCount(), 3):
                    task_desc_item = self.table.item(row, col)
                    task_name_item = self.table.item(row, col + 1)
                    grade_item = self.table.item(row, col + 2)

                    task_desc = task_desc_item.text() if task_desc_item else ''
                    task_name = task_name_item.text() if task_name_item else ''
                    grade = grade_item.text().strip() if grade_item else ''

                    if not task_name or not task_desc:
                        continue

                    try:
                        cursor.execute("""UPDATE TeacherInterface 
                                           SET grade = ? 
                                           WHERE student_login = ? AND task_name = ? AND date = ? 
                                           AND subject_name = ? AND student_class_name = ?""",
                                       (grade, student_login, task_name, current_date, subject_name, class_name))
                    except Exception as e:
                        QMessageBox.warning(self, "Error",
                                            f"Error while saving grade for student {student_login}: {str(e)}")

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Grades saved successfully.")
            self.load_class_data()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save changes: {str(e)}")

    def add_new_task(self):
        class_name = self.class_combo.currentText()
        if not class_name:
            QMessageBox.warning(self, "Warning", "Please select a class first.")
            return

        dialog = AddTaskDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            task_date, task_name, task_desc = dialog.get_task_data()

            success = self.save_task_for_all_students(class_name, task_date, task_name, task_desc)

            if success:
                if isinstance(task_date, str):
                    task_date = QDate.fromString(task_date, "yyyy-MM-dd")
                self.date_edit.setDate(task_date)

                self.load_class_data()

    def delete_task(self):
        class_name = self.class_combo.currentText()
        task_date = self.date_edit.date().toString("yyyy-MM-dd")

        if not class_name:
            QMessageBox.warning(self, "Warning", "Select a class first")
            return

        task_name, ok = QInputDialog.getText(self, "Delete Task", "Enter task name:")
        if ok and task_name:
            try:
                task_data = {
                    "name": task_name,
                    "class": class_name,
                    "date": task_date
                }
                self.tasks_list.delete(task_data)

                conn = pyodbc.connect(connection_string)
                cursor = conn.cursor()
                cursor.execute("""
                       DELETE FROM TeacherInterface 
                       WHERE student_class_name = ? AND task_name = ? AND date = ?
                   """, (class_name, task_name, task_date))

                if cursor.rowcount == 0:
                    QMessageBox.warning(self, "Warning", "Task not found.")
                    return

                conn.commit()
                QMessageBox.information(self, "Success", "Task deleted successfully.")
                self.load_class_data()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error deleting task: {str(e)}")
            finally:
                conn.close()
    def save_task_for_all_students(self, class_name, task_date, task_name, task_desc):
        try:
            if isinstance(task_date, str):
                task_date = datetime.strptime(task_date, "%Y-%m-%d")

            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()

            cursor.execute("SELECT subject_name FROM Teachers WHERE teacher_id = ?", (self.teacher_id,))
            subject_name = cursor.fetchone()[0]

            task_data = {
                "name": task_name,
                "description": task_desc,
                "date": task_date,
                "class": class_name,
                "subject": subject_name
            }
            self.tasks_list.append(task_data)

            cursor.execute("SELECT login FROM Students WHERE class_name = ?", (class_name,))
            students = cursor.fetchall()

            for student in students:
                cursor.execute("""
                       INSERT INTO TeacherInterface 
                       (student_login, task_name, task_description, date, student_class_name, subject_name)
                       VALUES (?, ?, ?, ?, ?, ?)
                   """, (student[0], task_name, task_desc, task_date, class_name, subject_name))

            conn.commit()
            QMessageBox.information(self, "Success", "Task added successfully.")
            return True

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return False
        finally:
            conn.close()

    def load_class_data(self):
        self.students_list = LinkedList()
        self.tasks_list = LinkedList()

        class_name = self.class_combo.currentText()
        task_date = self.date_edit.date().toString("yyyy-MM-dd")

        if not class_name:
            return

        try:
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()

            cursor.execute("SELECT login FROM Students WHERE class_name = ? ORDER BY login", (class_name,))
            students = cursor.fetchall()
            for student in students:
                self.students_list.append({"login": student[0], "class": class_name})

            cursor.execute("""
                SELECT DISTINCT task_name, task_description, date
                FROM TeacherInterface ti
                INNER JOIN Students s ON ti.student_login = s.login
                WHERE s.class_name = ? AND date = ? AND ti.subject_name = ?
                ORDER BY task_name
            """, (class_name, task_date, self.subject_name))

            tasks = cursor.fetchall()
            for task in tasks:
                self.tasks_list.append({
                    "name": task[0],
                    "description": task[1],
                    "date": task[2],
                    "class": class_name
                })

            # Prepare table for display
            # Iterate through the linked list instead of using len()
            student_count = 0
            student_node = self.students_list.head
            while student_node:
                student_count += 1
                student_node = student_node.next

            task_count = 0
            task_node = self.tasks_list.head
            while task_node:
                task_count += 1
                task_node = task_node.next

            self.table.setRowCount(student_count)
            self.table.setColumnCount(task_count * 3 + 2)

            headers = ['№', 'Student Login']
            for _ in range(task_count):
                headers.extend(['Task Description', 'Task Name', 'Grade'])
            self.table.setHorizontalHeaderLabels(headers)

            # Populate table with student and task data
            student_node = self.students_list.head
            for row in range(student_count):
                student = student_node.data
                index_item = QTableWidgetItem(str(row + 1))
                index_item.setFlags(index_item.flags() & ~Qt.ItemIsEditable)
                index_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 0, index_item)

                login_item = QTableWidgetItem(student["login"])
                login_item.setFlags(login_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 1, login_item)

                task_node = self.tasks_list.head
                for task_idx in range(task_count):
                    base_col = task_idx * 3 + 2
                    task = task_node.data

                    desc_item = QTableWidgetItem(task["description"])
                    desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row, base_col, desc_item)

                    task_name_item = QTableWidgetItem(f"{task['name']}")
                    task_name_item.setFlags(task_name_item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row, base_col + 1, task_name_item)

                    cursor.execute("""
                        SELECT grade FROM TeacherInterface 
                        WHERE student_login = ? AND task_name = ? AND date = ? AND subject_name = ?
                    """, (student["login"], task["name"], task_date, self.subject_name))
                    grade = cursor.fetchone()

                    grade_item = QTableWidgetItem(str(grade[0]) if grade else '')
                    self.table.setItem(row, base_col + 2, grade_item)

                    task_node = task_node.next

                student_node = student_node.next

            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.table.setAlternatingRowColors(True)
            self.table.verticalHeader().setVisible(False)
            self.table.setColumnWidth(0, 40)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading data: {str(e)}")
        finally:
            conn.close()


class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Task")
        self.setGeometry(100, 100, 400, 200)

        layout = QFormLayout()

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        layout.addRow("Task Date:", self.date_edit)

        self.task_name_edit = QLineEdit()
        layout.addRow("Task Name:", self.task_name_edit)

        self.task_desc_edit = QLineEdit()
        layout.addRow("Task Description:", self.task_desc_edit)

        self.save_button = QPushButton("Add Task")
        layout.addRow(self.save_button)

        self.setLayout(layout)

        self.save_button.clicked.connect(self.accept)

    def get_task_data(self):
        return self.date_edit.date().toString("yyyy-MM-dd"), self.task_name_edit.text(), self.task_desc_edit.text()


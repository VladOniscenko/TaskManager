import os
import sys

from functools import partial
from PySide6.QtCore import Qt
from PySide6.QtCore import QDateTime
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (QPushButton, QWidget, QVBoxLayout,
                               QScrollArea, QLabel, QMainWindow,
                               QApplication, QHBoxLayout, QDateTimeEdit,
                               QComboBox, QTextEdit, QLineEdit, QCheckBox, QSystemTrayIcon, QMenu)

from Controllers.agenda_controller import AgendaController
from Models.task import Task

WIDTH, HEIGHT = 300, 400
MAIN_BG_COLOR = '#1f1f1f'
SECOND_BG_COLOR = '#2a2a2a'
FALSE_BG_COLOR = 'rgba(77, 46, 46, 0.8)'
FALSE_TEXT_COLOR = 'lightcoral'
TRUE_BG_COLOR = 'rgba(46, 77, 46, 0.8)'
TRUE_TEXT_COLOR = 'lightgreen'


class MainWindow(QMainWindow):
    scroll_area: QScrollArea
    calendar: None | QDateTimeEdit
    show_hidden_tasks: QCheckBox
    show_all: QCheckBox
    count_label: QLabel

    extended_widget: QWidget
    extended_layout: QVBoxLayout

    priority_combo: QComboBox
    status_combo: QComboBox
    description_input: QTextEdit
    name_input: QLineEdit
    datetime_input: QDateTimeEdit

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Todo's Manager")
        self.setWindowIcon(QIcon(self.resource_path('assets/icon-w.png')))
        self.agenda = AgendaController(1)

        self.date = QDateTime.currentDateTime()
        self.tasks = []

        # creating main container main_widget
        self.main_widget = QWidget()
        self.main_widget.setObjectName('main_widget')
        self.main_widget.setFixedSize(300, 400)

        # add styling to our main widget
        self.main_widget.setStyleSheet(f"""
            QWidget#main_widget {{
                background-color: {MAIN_BG_COLOR};
            }}
        """)

        # create main layout positioning (vertical alignment)
        self.main_layout = QVBoxLayout(self.main_widget)

        # create header and add to our layout
        self.create_header()
        self.create_task_list()

        # Create the parent horizontal layout
        self.parent_layout_widget = QWidget()
        self.horizontal_layout = QHBoxLayout(self.parent_layout_widget)
        self.horizontal_layout.setSpacing(0)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)

        # Add main_widget to the horizontal layout
        self.horizontal_layout.addWidget(self.main_widget)

        # Set the parent layout widget as the central widget
        self.setCentralWidget(self.parent_layout_widget)

        # Initialize the system tray
        self.init_system_tray()

        # Make the window stay on top
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        # show widget
        self.show()

    @staticmethod
    def resource_path(relative_path):
        """
        Get the absolute path to a resource, depending on the execution environment.

        :param relative_path: The relative path to the resource.
        :return: The absolute path to the resource.
        """
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.abspath('.'))
        except AttributeError:
            base_path = os.path.abspath('.')

        return os.path.join(base_path, relative_path)

    def init_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('./assets/icon-w.png'))

        # Create tray menu
        tray_menu = QMenu()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)

        # Show tray icon
        self.tray_icon.show()

        # Handle double-click to show the window
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()

    def closeEvent(self, event):
        # ignore close event and hide window
        self.close_extended_tab()
        event.ignore()
        self.hide()

    def create_header(self):
        # create header layout type (horizontal layout)
        layout = QHBoxLayout()

        # calendar select box
        self.calendar = QDateTimeEdit(self.date)
        self.calendar.setDisplayFormat("dd-MM-yyyy")
        self.calendar.setCalendarPopup(True)
        self.calendar.dateChanged.connect(self.change_date)

        self.show_hidden_tasks = QCheckBox('Show all')
        self.show_hidden_tasks.clicked.connect(self.update_tasks_list)

        self.show_all = QCheckBox('Show all dates')
        self.show_all.setVisible(False)
        self.show_all.clicked.connect(self.update_tasks_list)

        # Create a vertical layout for checkboxes
        checkbox_layout = QVBoxLayout()
        checkbox_layout.addWidget(self.show_hidden_tasks)
        checkbox_layout.addWidget(self.show_all)

        # add our calendar to our layout
        layout.addWidget(self.calendar)
        layout.addLayout(checkbox_layout)

        # take all extra space for next widgets
        layout.addStretch()

        # Button to open "Create Task" window
        create_task_btn = QPushButton("+")  # create button with + as text
        create_task_btn.setFixedSize(30, 30)  # set button size
        create_task_btn.clicked.connect(
            self.open_create_task_window
        )  # set event function

        # add button to header layout
        layout.addWidget(create_task_btn)

        # add our created header layout to main layout
        self.main_layout.addLayout(layout)

    def open_task_info(self, _, task: Task):
        item_bg_color, item_text_color = task.status_color
        widget, layout = self.create_extended_tab(600)

        # Construct head of info widget
        head = QWidget()
        head_layout = QHBoxLayout(head)
        head_layout.setContentsMargins(0, 0, 0, 0)

        # create task head layout with status and close button
        task_status = QLabel(f'Task is {task.status}')
        task_status.setStyleSheet(f"""
            background-color: {item_bg_color};
            color: {item_text_color};
            text-transform: uppercase;
            font-weight: bold;
            padding: 10px;
            border: solid 1px {item_text_color};
            border-radius: 5px;
        """)

        head_layout.addWidget(task_status)

        # add priority to head
        item_bg_color, item_text_color = task.priority_color
        task_priority = QLabel(f'{task.priority} Priority')
        task_priority.setStyleSheet(f"""
            background-color: {item_bg_color};
            color: {item_text_color};
            text-transform: uppercase;
            font-weight: bold;
            padding: 10px;
            border: solid 1px {item_text_color};
            border-radius: 5px;
        """)
        head_layout.addWidget(task_priority)

        # stretch head for close button
        head_layout.addStretch()
        delete = QPushButton('Delete')
        delete.setStyleSheet("width: 50px; padding: 5px; border-radius: 5px;")

        # Add event listeners
        delete.mouseReleaseEvent = partial(self.delete_task, task_id=task.id)

        edit = QPushButton('Edit')
        edit.setStyleSheet(f"""
            width: 50px;
            padding: 5px;
            border-radius: 5px;
            background-color: {TRUE_BG_COLOR};
            color: {TRUE_TEXT_COLOR};
        """)

        # Add event listeners
        edit.mouseReleaseEvent = partial(
            self.open_create_task_window, task=task
        )

        close = QPushButton('X')
        close.setStyleSheet(f"""
            width: 50px;
            padding: 5px;
            border-radius: 5px;
            background-color: {FALSE_BG_COLOR};
            color: {FALSE_TEXT_COLOR};
        """)
        close.clicked.connect(self.close_extended_tab)

        head_layout.addWidget(delete)
        head_layout.addWidget(edit)
        head_layout.addWidget(close)
        layout.addWidget(head)

        # create task name
        task_name = QLabel(f'{task.name}')
        task_name.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
        """)
        task_name.setWordWrap(True)
        layout.addWidget(task_name)

        # add datetime
        d = task.get_datetime()
        task_date = QLabel(f'{d.strftime("%d %b %Y %H:%M")}')
        task_date.setWordWrap(True)
        layout.addWidget(task_date)

        # create task description
        task_description = QLabel(f'{task.description}')
        task_description.setStyleSheet("""
        """)
        task_description.setWordWrap(True)
        layout.addWidget(task_description)

        self.horizontal_layout.addWidget(widget)

        print(task)

    def mark_complete(self, _, task: Task):
        update = self.agenda.set_as_completed(task.id)
        if update['success']:
            print(f"Task marked as complete: {task.id}")
            self.update_tasks_list()
        else:
            print(f"{update['message']}")

    def create_task_list(self):
        try:
            if (
                    hasattr(self, 'count_label')
                    and self.count_label
                    and self.count_label.isWidgetType()
            ):
                self.count_label.deleteLater()
        except RuntimeError:
            pass

        # Create scrollable area
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName('task_list')

        # Create container where content will be placed
        scrollable_content = QWidget()
        scrollable_content.setObjectName('scroll_content')
        scrollable_content.setStyleSheet(f"""
            QWidget#scroll_content {{
                background: {MAIN_BG_COLOR};
            }}
        """)
        scrollable_content.setContentsMargins(0, 0, 0, 0)  # Set margins

        # Set layout to our container
        layout = QVBoxLayout(scrollable_content)
        layout.setContentsMargins(0, 0, 0, 0)  # Set margins
        layout.setSpacing(5)  # Optional: Add spacing between items

        if self.show_all.isChecked():
            get_tasks_response = self.agenda.get_tasks()
        else:
            active_tasks = not self.show_hidden_tasks.isChecked()
            get_tasks_response = self.agenda.get_tasks(
                self.date.toString('yyyy-MM-dd'),
                active_tasks=active_tasks
            )

        if get_tasks_response['success']:
            self.tasks = get_tasks_response['tasks']
        else:
            self.tasks = []

        if len(self.tasks) == 0:
            no_items_label = QLabel('No items found')
            no_items_label.setStyleSheet("""
                color: crimson;
                padding: 20px;
            """)
            layout.addWidget(no_items_label)
        else:
            self.count_label = QLabel(f'Tasks: {len(self.tasks)}')
            self.main_layout.addWidget(self.count_label)

            # Add items to the scrollable container layout
            for num, task in enumerate(self.tasks):
                if (
                    not self.show_hidden_tasks.isChecked()
                    and task.status in ('Cancelled', 'Completed')
                ):
                    continue

                # Create item container
                item_container = QWidget()

                # Set a unique object name
                item_container.setObjectName("itemContainer")
                item_container.setContentsMargins(15, 0, 15, 0)
                item_container.setFixedHeight(50)

                # get task colors
                item_bg_color, item_text_color = task.priority_color
                if task.status == 'Completed':
                    item_bg_color, _ = task.status_color

                item_container.setStyleSheet(f"""
                    QWidget#itemContainer {{
                        background-color: {item_bg_color};
                        color: {item_text_color};
                    }}

                    QWidget#itemContainer:hover {{
                        background-color: rgba(255, 255, 255, 0.15);
                    }}

                    QCheckBox#itemContainer {{
                        padding-right: 115px;
                    }}

                    QCheckBox::indicator {{
                        width: 20px;
                        height: 20px;
                        border-radius: 11px;
                        border: 1px solid gray;
                        background-color: rgba(255, 255, 255, 0.1);
                    }}

                    QCheckBox::indicator:unchecked {{
                        background-color: rgba(255, 255, 255, 0.1);
                    }}

                    QCheckBox::indicator:hover {{
                        background-color: rgba(46, 77, 46, 0.8);
                    }}
                """)

                # Set container layout
                item_layout = QHBoxLayout(item_container)
                item_layout.setContentsMargins(0, 0, 0, 0)

                if task.status != 'Completed':
                    # Add our item info to layout
                    checkbox = QCheckBox()
                    item_layout.addWidget(checkbox)
                    checkbox.mouseReleaseEvent = partial(
                        self.mark_complete, task=task
                    )

                task_name = task.name
                if len(task.name) > 25:
                    task_name = task.name[:25] + '...'

                text = QLabel(f'{task_name}')
                text.setStyleSheet(f"color: {item_text_color};")
                item_layout.addWidget(text)

                # Add stretch to push items to fill space
                item_layout.addStretch()

                time_label = QLabel(task.task_time_label)
                time_label.setObjectName('task_time_label')
                time_label.setStyleSheet(f"""
                    QLabel#task_time_label {{
                        color: {item_text_color};
                    }}
                """)

                item_layout.addWidget(time_label)

                # Add the item container to the scrollable layout
                layout.addWidget(item_container)

                # Add event listeners
                item_container.mouseReleaseEvent = partial(
                    self.open_task_info, task=task
                )

        # dont set spaces between items
        layout.addStretch()

        # Add our created content to the scrollable area
        self.scroll_area.setWidget(scrollable_content)

        # Ensure the widget resizes with the scroll area
        self.scroll_area.setWidgetResizable(True)

        # Add our scroll area to main content
        self.main_layout.addWidget(self.scroll_area)

    def open_create_task_window(self, _, task: Task = None):
        heading = 'Create Task'
        if task:
            heading = 'Edit Task'

        widget, layout = self.create_extended_tab(300)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # title and close button
        title = QLabel(heading)
        title.setStyleSheet("""
            font-weight: bold;
            font-size: 20px;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()

        close = QPushButton('X')
        close.clicked.connect(self.close_extended_tab)
        close.setStyleSheet(f"""
            width: 50px;
            padding: 5px;
            border-radius: 5px;
            background-color: {FALSE_BG_COLOR};
            color: {FALSE_TEXT_COLOR};
        """)
        header_layout.addWidget(close)

        layout.addWidget(header)  # add header to layout

        # Create form to add task
        create_form = QWidget()
        create_form_layout = QVBoxLayout(create_form)
        create_form_layout.setContentsMargins(0, 0, 0, 0)
        create_form_layout.setSpacing(10)  # Space between form elements

        # Name input
        self.name_input = QLineEdit()  # Name input
        self.name_input.setPlaceholderText("Name...")
        if task:
            self.name_input.setText(task.name)
        create_form_layout.addWidget(self.name_input)

        # Description input
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Description...")
        self.description_input.setFixedHeight(75)
        if task:
            self.description_input.setText(task.description)
        create_form_layout.addWidget(self.description_input)

        # Status input
        self.status_combo = QComboBox()
        self.status_combo.addItems(Task.statuses())  # Example items
        if task:
            self.status_combo.setCurrentIndex(
                self.status_combo.findText(task.status)
            )
        create_form_layout.addWidget(self.status_combo)

        # Priority input
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(Task.priorities())  # Example items
        if task:
            self.priority_combo.setCurrentIndex(
                self.priority_combo.findText(task.priority)
            )
        create_form_layout.addWidget(self.priority_combo)

        # Datetime input
        self.datetime_input = QDateTimeEdit()
        self.datetime_input.setDateTime(
            QDateTime.currentDateTime().addSecs(3600)
        )  # Set initial value to 1 hour ahead
        self.datetime_input.setCalendarPopup(True)  # Enable the calendar popup
        if task:
            self.datetime_input.setDateTime(
                QDateTime.fromSecsSinceEpoch(
                    int(task.get_datetime().timestamp())
                )
            )
        create_form_layout.addWidget(self.datetime_input)

        # Submit button
        submit_button = QPushButton("Submit")
        submit_button.setStyleSheet(f"""
            background-color: {TRUE_BG_COLOR};
            color: {TRUE_TEXT_COLOR};
            padding: 10px;
            border-radius: 5px;
            border: none;
        """)
        submit_button.mouseReleaseEvent = partial(self.submit_task, task=task)
        create_form_layout.addWidget(submit_button)

        layout.addWidget(create_form)

        # Global form stylesheet
        create_form.setStyleSheet(f"""
            QLineEdit, QTextEdit, QComboBox, QDateTimeEdit {{
                background-color: {SECOND_BG_COLOR};
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #666;
            }}
        """)

    def update_tasks_list(self):
        self.scroll_area.deleteLater()
        self.create_task_list()

    def change_date(self, new_date):
        # Handle the selected date
        print(f"Selected date: {new_date.toString('dd-MM-yyyy')}")

        self.date = new_date
        self.update_tasks_list()

    def create_extended_tab(self, w: int = 750):
        # check if it is created
        try:
            if (hasattr(self, 'extended_widget')
                    and self.extended_widget
                    and self.extended_widget.isWidgetType()):
                self.extended_widget.deleteLater()
        except RuntimeError:
            # Handle the case when the widget has already been deleted
            pass

        # Add a layout for the extended_widget
        self.extended_widget = QWidget()
        self.extended_layout = QVBoxLayout(self.extended_widget)
        self.extended_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.extended_widget.setObjectName("createWidget")
        self.extended_widget.setStyleSheet(f"""
            QWidget#createWidget {{
                background-color: {SECOND_BG_COLOR};
            }}
        """)

        self.setFixedWidth(WIDTH + w)
        self.horizontal_layout.addWidget(self.extended_widget)
        return self.extended_widget, self.extended_layout

    def close_extended_tab(self):
        try:
            if (hasattr(self, 'extended_widget')
                    and self.extended_widget is not None):
                self.extended_widget.deleteLater()
        except RuntimeError:
            # Handle the case when the widget has already been deleted
            pass
        self.setFixedWidth(WIDTH)

    def submit_task(self, _, task: Task = None):
        name = self.name_input.text()
        description = self.description_input.toPlainText()
        selected_status = self.status_combo.currentText()
        selected_priority = self.priority_combo.currentText()
        date = self.datetime_input.dateTime().toPython()

        # check if inputs are not empty
        if (name == '' or selected_status == '' or
                selected_priority == '' or date == ''):
            return

        if task:
            action_response = self.agenda.update_task(
                task.id, name, description,
                date, selected_priority, selected_status
            )
        else:
            # create task
            action_response = self.agenda.add_task(
                name, description, date,
                selected_priority, selected_status
            )

        if not action_response['success']:
            print(action_response['message'])
            return

        task = action_response['task']
        if task:
            print(f'Task updated! id: {task.id}')
        else:
            print(f"Task created! id: {task.id}")

        self.close_extended_tab()
        self.update_tasks_list()

    def delete_task(self, _, task_id: int):
        action_response = self.agenda.delete_task(task_id)
        if action_response['success']:
            print(f'Task deleted! id: {task_id}')
        else:
            print(action_response['message'])

        self.close_extended_tab()
        self.update_tasks_list()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.setFixedSize(WIDTH, HEIGHT)
    window.move(0, 0)

    sys.exit(app.exec())

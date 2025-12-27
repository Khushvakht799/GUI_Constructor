# src/gui/gui_main.py
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTextEdit
from core.app_core import AppCore

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.core = AppCore()        # <--- связь GUI ↔ Core
        self.setWindowTitle("GUI Constructor")

        layout = QVBoxLayout(self)

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        btn_load = QPushButton("Выбрать каталог проекта")
        btn_generate = QPushButton("Сгенерировать GUI")

        btn_load.clicked.connect(self.load_project)
        btn_generate.clicked.connect(self.generate_gui)

        layout.addWidget(btn_load)
        layout.addWidget(btn_generate)
        layout.addWidget(self.log)

    def load_project(self):
        path = QFileDialog.getExistingDirectory(self, "Выбор каталога проекта")
        if path:
            self.core.load_project(path)
            self.log.append(f"Выбран проект: {path}")

    def generate_gui(self):
        result = self.core.generate_gui_for_project()
        self.log.append(result)


def run():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
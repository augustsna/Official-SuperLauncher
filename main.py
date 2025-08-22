import sys
from PySide6.QtWidgets import QApplication, QLabel, QPushButton

from template_app.ui.main_window_base import MainWindowBase


class DemoWindow(MainWindowBase):
    def __init__(self):
        super().__init__()

def main():
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()



from PySide6.QtWidgets import (
    QApplication,
)
import sys

from modelview import MainWindowList


app = QApplication(sys.argv)

w = MainWindowList()
w.show()

app.exec()

from PySide6.QtWidgets import (
    QApplication,
)
import sys

from outdated.mainwindow import MainWindow


app = QApplication(sys.argv)

w = MainWindow()
w.show()

app.exec()

# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ListWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QLabel,
    QLineEdit, QListView, QMainWindow, QMenuBar,
    QProgressBar, QPushButton, QSizePolicy, QStatusBar,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(366, 475)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.referenceLabel = QLabel(self.centralwidget)
        self.referenceLabel.setObjectName(u"referenceLabel")

        self.verticalLayout.addWidget(self.referenceLabel)

        self.referenceEdit = QLineEdit(self.centralwidget)
        self.referenceEdit.setObjectName(u"referenceEdit")

        self.verticalLayout.addWidget(self.referenceEdit)

        self.referenceAddButton = QPushButton(self.centralwidget)
        self.referenceAddButton.setObjectName(u"referenceAddButton")

        self.verticalLayout.addWidget(self.referenceAddButton)

        self.distordedLabel = QLabel(self.centralwidget)
        self.distordedLabel.setObjectName(u"distordedLabel")

        self.verticalLayout.addWidget(self.distordedLabel)

        self.distordedView = QListView(self.centralwidget)
        self.distordedView.setObjectName(u"distordedView")
        self.distordedView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.verticalLayout.addWidget(self.distordedView)

        self.progress = QProgressBar(self.centralwidget)
        self.progress.setObjectName(u"progress")
        self.progress.setValue(0)

        self.verticalLayout.addWidget(self.progress)

        self.speed = QLabel(self.centralwidget)
        self.speed.setObjectName(u"speed")

        self.verticalLayout.addWidget(self.speed)

        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.distordedAddButton = QPushButton(self.widget)
        self.distordedAddButton.setObjectName(u"distordedAddButton")

        self.horizontalLayout.addWidget(self.distordedAddButton)

        self.distoredRemoveButton = QPushButton(self.widget)
        self.distoredRemoveButton.setObjectName(u"distoredRemoveButton")

        self.horizontalLayout.addWidget(self.distoredRemoveButton)

        self.runButton = QPushButton(self.widget)
        self.runButton.setObjectName(u"runButton")

        self.horizontalLayout.addWidget(self.runButton)


        self.verticalLayout.addWidget(self.widget)

        self.showPlotButton = QPushButton(self.centralwidget)
        self.showPlotButton.setObjectName(u"showPlotButton")

        self.verticalLayout.addWidget(self.showPlotButton)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 366, 24))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Todo", None))
        self.referenceLabel.setText(QCoreApplication.translate("MainWindow", u"Reference", None))
        self.referenceAddButton.setText(QCoreApplication.translate("MainWindow", u"Add Reference File", None))
        self.distordedLabel.setText(QCoreApplication.translate("MainWindow", u"Distorded videos", None))
        self.speed.setText(QCoreApplication.translate("MainWindow", u"FPS", None))
        self.distordedAddButton.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.distoredRemoveButton.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.runButton.setText(QCoreApplication.translate("MainWindow", u"Run !", None))
        self.showPlotButton.setText(QCoreApplication.translate("MainWindow", u"Show Plots", None))
    # retranslateUi


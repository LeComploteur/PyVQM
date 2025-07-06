from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
    QProgressBar,
    QLabel,
    QTabWidget,
)

import pyqtgraph as pg


class PlotWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()

        # Create 3 plot widgets for SSIM, PSNR, and VMAF, for each video
        self.graphWidgetSSIM = pg.PlotWidget()
        self.graphWidgetPSNR = pg.PlotWidget()
        self.graphWidgetVMAF = pg.PlotWidget()

        # Create a tab widget to hold the plot widgets
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(True)

        # Add the plot widgets to the tab widget
        self.tabs.addTab(self.graphWidgetSSIM, "SSIM")
        self.tabs.addTab(self.graphWidgetPSNR, "PSNR")
        self.tabs.addTab(self.graphWidgetVMAF, "VMAF")

        # Set the layout for the main window
        self.setCentralWidget(self.tabs)

        # Set the window title and size
        self.setWindowTitle("Plotting Values")

        # Initialize the data for the plots
        self.x = []
        self.y = []

        # Set the style for plotting
        self.graphWidgetSSIM.setBackground("#676e69")
        self.graphWidgetPSNR.setBackground("w")
        self.graphWidgetVMAF.setBackground("w")

        # Set the style for the lines
        pen = pg.mkPen(color=(255, 0, 0))

        self.graphWidgetPSNR.addLegend()
        self.graphWidgetVMAF.addLegend()
        self.graphWidgetSSIM.addLegend()

        self.data_linesSSIM = []
        self.data_linesPSNR = []
        self.data_linesVMAF = []

        self.pens = [
            pg.mkPen(color=(255, 0, 0)),
            pg.mkPen(color=(0, 255, 0)),
            pg.mkPen(color=(0, 0, 255)),
        ]


    def reset_all(self, index):
        self.data_linesSSIM[index].clear()
        self.data_linesPSNR[index].clear()
        self.data_linesVMAF[index].clear()

    def add_plot(self, name: str):
        len_data_lines = len(self.data_linesSSIM)
        self.data_linesSSIM.append(
            self.graphWidgetSSIM.plot(self.x, self.y, pen=self.pens[len_data_lines], name=name))
        self.data_linesPSNR.append(
            self.graphWidgetPSNR.plot(self.x, self.y, pen=self.pens[len_data_lines], name=name))
        self.data_linesVMAF.append(
            self.graphWidgetVMAF.plot(self.x, self.y, pen=self.pens[len_data_lines], name=name))
        
    def remove_plot(self, index):
        if index < len(self.data_linesSSIM):
            self.graphWidgetSSIM.removeItem(self.data_linesSSIM[index])
            self.graphWidgetPSNR.removeItem(self.data_linesPSNR[index])
            self.graphWidgetVMAF.removeItem(self.data_linesVMAF[index])
            del self.data_linesSSIM[index]
            del self.data_linesPSNR[index]
            del self.data_linesVMAF[index]

    def reset_ssim(self, index):
        self.data_linesSSIM[index].clear()

    def reset_psnr(self, index):
        self.data_linesPSNR[index].clear()

    def reset_vmaf(self, index):
        self.data_linesVMAF[index].clear()

    def update_SSIM_data(self, x, y, index):
        self.data_linesSSIM[index].setData(x, y)

    def update_PSNR_data(self, x, y, index):
        self.data_linesPSNR[index].setData(x, y)

    def update_VMAF_data(self, x, y, index):
        self.data_linesVMAF[index].setData(x, y)

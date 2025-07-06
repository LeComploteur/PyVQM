import logging
import sys

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QProcess, Qt
from rich.logging import RichHandler

from ListWindow import Ui_MainWindow
from metrics_parser import parse_psnr_values, parse_ssim_values, simple_fps_parser
from plotwindows import PlotWindow
from video import Distorded, Reference

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")


# Load the tick icon.
tick = QtGui.QImage("tick.png")


class DistordedModel(QtCore.QAbstractListModel):
    def __init__(self, *args, todos=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.distordedList: list[Distorded] = []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            distorded = self.distordedList[index.row()]

            return distorded.video_path

        if role == Qt.DecorationRole:
            distorded = self.distordedList[index.row()]
            status = distorded.ssim_computed
            if not status:
                return tick

    def rowCount(self, index):
        return len(self.distordedList)


class MainWindowList(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.__init_ui___()

        self.model = DistordedModel()
        self.distordedView.setModel(self.model)

        self.plotWindow = PlotWindow(self)  # Reference to the plot window.

        self.stdout_buffer = ""  # Buffer pour stocker les données partielles
        self.all_ssim_values = []  # Pour stocker toutes les valeurs SSIM

        self.SSIM_frames = []  # Liste pour stocker les frames
        self.ssim_values = []  # Liste pour stocker les valeurs SSIM

        self.psnr_frames = []  # Liste pour stocker les frames PSNR
        self.psnr_values = []  # Liste pour stocker les valeurs PSNR

        

        self.p = None  # Initialize the QProcess to None as we don't have any running processes at start.

    def __init_ui___(self):
        # Connect the add reference button
        self.distordedAddButton.pressed.connect(self.addDistoreded)
        # Connect the add distored button
        self.referenceAddButton.pressed.connect(self.addReference)
        # Connect the remove distorded button
        self.distoredRemoveButton.pressed.connect(self.delete)
        # Connect the Show plots button
        self.showPlotButton.clicked.connect(self.show_new_window)
        # Connect the run button
        self.runButton.pressed.connect(self.start_compute)
        self.setAcceptDrops(True)
        # self.distordedView.setAcceptDrops(True)

    def addDistoreded(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "Text Files (*.mp4;*.mkv;*.avi;*.ogv,*.mov);;All Files (*)",
            options=options,
        )
        if file_name:
            log.debug(f"Adding distorded file: {file_name}")
            # Create a Distorded object and append it to the model
            distorded = Distorded(file_name)
            self.model.distordedList.append(distorded)
            self.plotWindow.add_plot(distorded.video_path)
            self.runButton.setEnabled(True)

            self.runButton.setText("Run !")
            self.model.layoutChanged.emit()

        return

    def addReference(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "Text Files (*.mp4;*.mkv;*.avi;*.ogv,*.mov);;All Files (*)",
            options=options,
        )
        if file_name:
            log.debug(f"Reference file selected is now: {file_name}")
            self.reference = Reference(file_name)
            self.referenceEdit.setText(f"{self.reference.video_path}")
            # Make sure to reanable the run button
            self.runButton.setEnabled(True)
            self.runButton.setText("Run !")
            self.model.layoutChanged.emit()
            # TODO : Clear all plots if we chhange the reference
        return

    def showPlots(self):
        return

    def add(self):
        """
        Add an item to our todo list, getting the text from the QLineEdit .todoEdit
        and then clearing it.
        """
        text = self.todoEdit.text()
        if text:  # Don't add empty strings.
            # Access the list via the model.
            self.model.distordedList.append((False, text))
            # Trigger refresh.
            self.model.layoutChanged.emit()
            # Empty the input
            self.todoEdit.setText("")

    def delete(self):
        indexes = self.distordedView.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            # Remove the item and refresh.
            del self.model.distordedList[index.row()]
            self.model.layoutChanged.emit()
            # Clear the selection (as it is no longer valid).
            self.distordedView.clearSelection()
            self.plotWindow.remove_plot(index.row())

    def show_new_window(self, checked):
        """
        Toggles the visibility of the plot window and updates the button text accordingly.

        Args:
            checked: A boolean indicating whether the showPlotButton is in a checked state.
                     This parameter is not used within this function but is required by the
                     signal-slot connection.

        Returns:
            None
        """
        if self.plotWindow.isVisible():
            self.plotWindow.hide()
            self.showPlotButton.setText("Show plot")
        else:
            self.plotWindow.show()
            self.showPlotButton.setText("Hide plot")

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        """
        Drop files directly onto the widget
        File locations are stored in fname
        :param e:
        :return:
        """
        if e.mimeData().hasUrls:
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
            # Workaround for OSx dragging and dropping
            for url in e.mimeData().urls():
                file_path = str(url.toLocalFile())
                log.info(f"Got {file_path} drag & dropped into the window")
                # Create a Distorded object and append it to the model
                distorded = Distorded(file_path)
                self.model.distordedList.append(distorded)
                self.plotWindow.add_plot(distorded.video_path)
                self.runButton.setEnabled(True)
                self.runButton.setText("Run !")
                self.model.layoutChanged.emit()

        else:
            e.ignore()

    def closeEvent(self, event):
        if self.plotWindow:
            self.plotWindow.close()

        if self.p is not None and self.p.state() != QProcess.NotRunning:
            log.info("Closing MainWindow, killing process...")
            self.p.kill()
            self.p.waitForFinished()
            self.p = None

    def run(self):
        """
        Run the application.
        """
        distordedList = self.model.distordedList
        for distorded in distordedList:
            log.info(f"Got to run on {distorded.video_path}")

    """  
    Function to start a new process with the given arguments and connect the signals to the handlers.
            This function is used to start both SSIM and PSNR processes.
            It takes the following parameters:
            - plot_to_reset: function to reset the plot
            - stdout_handler: function to handle standard output, produced by FFMpeg 
            - std_err_handler: function to handle standard error
            - p_finished_handler: function to handle process finished signal
            - frames_data: list to store frames data
            - fps_data: list to store fps data
            - args: list of arguments for the process
            - index: index of the video being processed
    """

    def start_process(
        self,
        plot_to_reset,
        stdout_handler,
        std_err_handler,
        p_finished_handler,
        frames_data: list,
        fps_data: list,
        args: list = [],
        index: int = 0,
    ):
        frames_data.clear()
        fps_data.clear()
        # Before we plot, make sure to reset the plot
        plot_to_reset(index)
        # Reset the values stored in the lists
        frames_data.clear()
        fps_data.clear()
        # Clear the buffer
        self.stdout_buffer = ""
        # Create a new QProcess instance
        self.p = QProcess()

        self.p.readyReadStandardOutput.connect(stdout_handler)
        self.p.readyReadStandardError.connect(std_err_handler)
        self.p.stateChanged.connect(self.handle_state)
        self.p.finished.connect(
            lambda exitCode, exitStatus: p_finished_handler(
                self.p, index, exitCode, exitStatus
            )
        )
        self.p.start(
            "ffmpeg",
            args,
        )

    def start_SSIM(self, index):
        # Build the arguments for SSIM for the given index
        args = [
            "-i",
            self.model.distordedList[index].video_path,
            "-t",
            "60",
            "-i",
            self.reference.video_path,
            "-t",
            "60",
            "-lavfi",
            "ssim=stats_file=-",
            "-f",
            "null",
            "-",
        ]

        self.start_process(
            self.plotWindow.reset_ssim,
            lambda: self.handle_stdout_SSIM(index),
            self.handle_stderr_SSIM,
            self.SSIM_finished,
            self.model.distordedList[index].frames,
            self.model.distordedList[index].ssim_values,
            args,
            index,
        )

    def start_PSNR(self, index):
        # Build the arguments for SSIM for the given index
        args = [
            "-i",
            self.model.distordedList[index].video_path,
            "-t",
            "60",
            "-i",
            self.reference.video_path,
            "-t",
            "60",
            "-lavfi",
            "psnr=stats_file=-",
            "-f",
            "null",
            "-",
        ]

        self.start_process(
            self.plotWindow.reset_psnr,
            lambda: self.handle_stdout_PSNR(index),
            self.handle_stderr_PSNR,
            self.PSNR_finished,
            self.psnr_frames,
            self.psnr_values,
            args,
            index,
        )

    def handle_stderr(self, process: QProcess):
        data = process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        # Extract progress if it is in the data.
        speed = simple_fps_parser(stderr)
        if speed:
            self.speed.setText(f"Fps: {speed}")
        else:
            # self.message(stderr)
            pass

    def handle_stderr_SSIM(self):
        self.handle_stderr(self.p)

    def handle_stderr_PSNR(self):
        self.handle_stderr(self.p)

    def handle_stdout(
        self,
        process: QProcess,
        frames_data: list,
        fps_data: list,
        plot_to_update,
        index,
        parser,
        metric_to_update: str,
    ):
        data = process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")

        # Ajouter les nouvelles données au buffer
        self.stdout_buffer += stdout

        # Traiter chaque ligne complète
        lines = self.stdout_buffer.split("\n")
        # Garder la dernière ligne potentiellement incomplète dans le buffer
        self.stdout_buffer = lines.pop() if lines else ""

        for line in lines:
            if line.strip():  # Ignorer les lignes vides
                ssim_values = parser(line)
                if ssim_values:
                    frames_data.append(ssim_values["frame"])
                    fps_data.append(ssim_values["All"])
                    getattr(self.model.distordedList[index], metric_to_update).append(
                        ssim_values["All"]
                    )
                    if not (
                        self.model.distordedList[index].ssim_computed
                        or self.model.distordedList[index].psnr_computed
                    ):
                        getattr(
                            self.model.distordedList[index],"frames"
                        ).append(ssim_values["frame"])
                    """ self.model.distordedList[index].frames.append(ssim_values["frame"])
                    self.model.distordedList[index].ssim_values.append(
                        ssim_values["All"]
                    )
 """
                    # TODO : Broken since we compute multiple times
                    # Mettre à jour la barre de progression si vous connaissez le nombre total de frames
                    # Si vous connaissez le nombre total de frames (total_frames):
                    self.progress.setValue(int(ssim_values["frame"] * 100 / 5202))
                    plot_to_update(
                        frames_data, fps_data, index
                    )  # Mettre à jour le graphique

    def handle_stdout_SSIM(self, index):
        self.handle_stdout(
            self.p,
            self.SSIM_frames,
            self.ssim_values,
            self.plotWindow.update_SSIM_data,
            index,
            parse_ssim_values,
            "ssim_values",
        )

    def handle_stdout_PSNR(self, index):
        self.handle_stdout(
            self.p,
            self.psnr_frames,
            self.psnr_values,
            self.plotWindow.update_PSNR_data,
            index,
            parse_psnr_values,
            "psnr_values",
        )

    def handle_state(self, state):
        states = {
            QProcess.NotRunning: "Not running",
            QProcess.Starting: "Starting",
            QProcess.Running: "Running",
        }
        state_name = states[state]
        # self.message(f"State changed: {state_name}")

    def process_finished(self, process: QProcess):

        log.info("Got into process_finished")
        if self.p is not None:
            log.info("self.p is NOT None, process is stil running. Aborting")
            return

        if getattr(self, "p", None) is None:
            # Iterate over distorted videos to check SSIM computation
            for index, distorted_video in enumerate(self.model.distordedList):
                if not distorted_video.ssim_computed:
                    self.start_SSIM(index=index)
                    log.info(f"Starting SSIM for index {index}")
                    return  # Exit the method after starting the process
            # If all SSIM computations are done, check PSNR
            for index, distorted_video in enumerate(self.model.distordedList):
                if not distorted_video.psnr_computed:
                    self.start_PSNR(index=index)
                    log.info(f"Starting PSNR for index {index}")
                    return  # Exit the method after starting the process

            # self.message("All process completed. Nothing to do")
            log.info("All process completed. Hanging out, chill there")
            self.runButton.setText("All done")
            self.runButton.pressed.disconnect()
            self.runButton.pressed.connect(self.start_compute)
            self.runButton.setEnabled(False)

    def SSIM_finished(self, p: QProcess, index: int, exitCode, exitStatus):
        if self.p is None:
            # If we are here, it means the process is killed
            log.info("Process killed in SSIM_finished, exiting")
            return

        if exitStatus == QProcess.ExitStatus.NormalExit and exitCode == 0:
            # self.message("SSIM process finished successfully.")
            log.info(f"Setting ssim_computed  for index {index} to True")
            self.model.distordedList[index].ssim_computed = True
            self.p.waitForFinished()
            self.p = None
            self.process_finished(p)
        else:
            log.error("SSIM process finished with an error.")
            log.info(f"Setting ssim_computed  for index {index} to False")
            self.model.distordedList[index].ssim_computed = False
            return  # Stop the process if it crashed

    def PSNR_finished(self, p: QProcess, index: int, exitCode, exitStatus):
        if self.p is None:
            # If we are here, it means the process is killed
            log.info("Process killed in PSNR_finished, exiting")
            return

        if exitStatus == QProcess.ExitStatus.NormalExit and exitCode == 0:
            # self.message("PSNR process finished successfully.")
            log.info(f"Setting psnr_computed  for index {index} to True")
            self.model.distordedList[index].psnr_computed = True
            self.p.waitForFinished()
            self.p = None
            self.process_finished(p)

        else:
            log.error("PSNR process finished with an error.")
            log.info(f"Setting psnr_computed  for index {index} to False")
            self.model.distordedList[index].psnr_computed = False
            return

    def start_compute(self):
        self.stop = False
        self.runButton.setText("Stop")
        self.runButton.pressed.disconnect()
        self.runButton.pressed.connect(self.stop_compute)
        self.process_finished(self.p)

    def stop_compute(self):
        if self.p is not None and self.p.state() != QProcess.NotRunning:
            log.info("Stopping process...")
            self.p.kill()
            self.p.waitForFinished()
            self.p = None
        else:
            log.info("No process is running to stop.")
        self.runButton.setText("Execute")
        self.runButton.pressed.disconnect()
        self.runButton.pressed.connect(self.start_compute)




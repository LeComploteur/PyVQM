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

from plotwindows import PlotWindow
from PySide6.QtCore import QProcess

from metrics_parser import parse_psnr_values, parse_ssim_values, simple_fps_parser
from collections import deque  # Import the deque class
from video import Reference, Distorded

import logging
from rich.logging import RichHandler

from typing import Callable

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")
log.info("Hello, World!")

SSIM_ARGS = [
    "-i",
    "D:\\Untitled.mp4",
    "-i",
    "D:\\Untitled2.mp4",
    "-lavfi",
    "ssim=stats_file=-",
    "-f",
    "null",
    "-",
]


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__()
        self.__init_ui___()

        self.stdout_buffer = ""  # Buffer pour stocker les données partielles
        self.all_ssim_values = []  # Pour stocker toutes les valeurs SSIM

        self.SSIM_frames = []  # Liste pour stocker les frames
        self.ssim_values = []  # Liste pour stocker les valeurs SSIM

        self.psnr_frames = []  # Liste pour stocker les frames PSNR
        self.psnr_values = []  # Liste pour stocker les valeurs PSNR

        self.reference = Reference("/home/hugo/Documents/Compare/BFV_ref.mp4")
        self.distorted = []
        for i in range(3):
            distorted = Distorded(f"/home/hugo/Documents/Compare/BFV_{i+1}.mp4")
            self.distorted.append(distorted)
            self.plotWindow.add_plot(distorted.video_path)

        self.p = None  # Initialize the QProcess to None as we don't have any running processes at start.

    def __init_ui___(self):

        self.btn = QPushButton("Execute")
        self.btn.pressed.connect(self.start_compute)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.speed = QLabel(text="Fps: N/A")
        self.btn_show_plot = QPushButton("Show plot")

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)

        l = QVBoxLayout()
        l.addWidget(self.btn)
        l.addWidget(self.progress)
        l.addWidget(self.speed)
        l.addWidget(self.text)
        l.addWidget(self.btn_show_plot)

        self.btn_show_plot.clicked.connect(self.show_new_window)
        self.plotWindow = PlotWindow(self)  # Reference to the plot window.

        w = QWidget()
        w.setLayout(l)
        self.setCentralWidget(w)

    def closeEvent(self, event):
        if self.plotWindow:
            self.plotWindow.close()

    def show_new_window(self, checked):
        if self.plotWindow.isVisible():
            self.plotWindow.hide()
            self.btn_show_plot.setText("Show plot")
        else:
            self.plotWindow.show()
            self.btn_show_plot.setText("Hide plot")

    def message(self, s):
        pass
        # self.text.appendPlainText(s)

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
            self.distorted[index].video_path,
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
            self.SSIM_frames,
            self.ssim_values,
            args,
            index,
        )

    def start_PSNR(self, index):
        # Build the arguments for SSIM for the given index
        args = [
            "-i",
            self.distorted[index].video_path,
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
        )

    def handle_stdout_PSNR(self, index):
        self.handle_stdout(
            self.p,
            self.psnr_frames,
            self.psnr_values,
            self.plotWindow.update_PSNR_data,
            index,
            parse_psnr_values,
        )

    def handle_state(self, state):
        states = {
            QProcess.NotRunning: "Not running",
            QProcess.Starting: "Starting",
            QProcess.Running: "Running",
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    def process_finished(self, process: QProcess):

        log.info("Got into process_finished")
        if self.p is not None:
            log.info("self.p is NOT None, process is stil running. Aborting")
            return

        if getattr(self, "p", None) is None:
            # Iterate over distorted videos to check SSIM computation
            for index, distorted_video in enumerate(self.distorted):
                if not distorted_video.ssim_computed:
                    self.start_SSIM(index=index)
                    log.info(f"Starting SSIM for index {index}")
                    return  # Exit the method after starting the process
            # If all SSIM computations are done, check PSNR
            for index, distorted_video in enumerate(self.distorted):
                if not distorted_video.psnr_computed:
                    self.start_PSNR(index=index)
                    log.info(f"Starting PSNR for index {index}")
                    return  # Exit the method after starting the process

            self.message("All process completed. Nothing to do")
            log.info("All process completed. Hanging out, chill there")
            self.btn.setText("All done")
            self.btn.pressed.disconnect()
            self.btn.setEnabled(False)

    def SSIM_finished(self, p: QProcess, index: int, exitCode, exitStatus):
        if self.p is None:
            # If we are here, it means the process is killed
            log.info("Process killed in SSIM_finished, exiting")
            return

        if exitStatus == QProcess.ExitStatus.NormalExit and exitCode == 0:
            self.message("SSIM process finished successfully.")
            log.info(f"Setting ssim_computed  for index {index} to True")
            self.distorted[index].ssim_computed = True
            self.p.waitForFinished()
            self.p = None
            self.process_finished(p)
        else:
            log.error("SSIM process finished with an error.")
            log.info(f"Setting ssim_computed  for index {index} to False")
            self.distorted[index].ssim_computed = False
            return  # Stop the process if it crashed

    def PSNR_finished(self, p: QProcess, index: int, exitCode, exitStatus):
        if self.p is None:
            # If we are here, it means the process is killed
            log.info("Process killed in PSNR_finished, exiting")
            return

        if exitStatus == QProcess.ExitStatus.NormalExit and exitCode == 0:
            self.message("PSNR process finished successfully.")
            log.info(f"Setting psnr_computed  for index {index} to True")
            self.distorted[index].psnr_computed = True
            self.p.waitForFinished()
            self.p = None
            self.process_finished(p)

        else:
            log.error("PSNR process finished with an error.")
            log.info(f"Setting psnr_computed  for index {index} to False")
            self.distorted[index].psnr_computed = False
            return

    def start_compute(self):
        self.stop = False
        self.btn.setText("Stop")
        self.btn.pressed.disconnect()
        self.btn.pressed.connect(self.stop_compute)
        self.process_finished(self.p)

    def stop_compute(self):
        if self.p is not None and self.p.state() != QProcess.NotRunning:
            log.info("Stopping process...")
            self.p.kill()
            self.p.waitForFinished()
            self.p = None
        else:
            log.info("No process is running to stop.")
        self.btn.setText("Execute")
        self.btn.pressed.disconnect()
        self.btn.pressed.connect(self.start_compute)

from collections import deque  # Import the deque class
from PySide6.QtCore import QProcess, QTimer   # Required imports from PySide6 for handling processes and timers respectively.
import sys    # For system-specific parameters and functions (like exit codes)

class ProcessQueue:
    def __init__(self):
        self.queue = deque()  # Create a new empty queue of process commands/arguments pairs
        self.current_process = None   # Initialize the current process to None as we don't have any running processes at start.

    def add(self, command, args=[]):
        """Adds a QProcess object with given `command` and arguments to queue."""
        self.queue.append((command, args))   # Appending tuple of command and argument in the deque (queue).
        if not self.current_process:  # If there's no process currently running...
            self.run()    # ... then start one right away!

    def run(self):
        """Starts next available QProcess object."""
        if self.current_process and self.current_process.state() == QProcess.Running:  # If there's a process running already...
            return   # ... then don't start any new ones until it finishes!
        elif len(self.queue) > 0:    # Else, if the queue is not empty....
            command, args = self.queue.popleft()  # Pop (remove and return) leftmost element from deque (command & arguments pair).
            self.current_process = QProcess()   # Initialize a new process object...
            self.current_process.finished.connect(self.run)    # ... connect its "finished" signal to our run method, so that next process in the queue will start automatically when this one finishes...
            self.current_process.start(command, args)  # And finally start it!
        else:   # If there's nothing left in the queue....
            sys.exit()    # ... then exit our application gracefully (or do anything you want).
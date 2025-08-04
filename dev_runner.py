# dev_runner.py

import os
import subprocess
import sys
import time

from PyQt5.QtWidgets import QApplication
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
app = QApplication(sys.argv)

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command
        self.process = None
        self.start_process()

    def start_process(self):
        # Bắt đầu tiến trình mới
        self.process = subprocess.Popen(self.command, shell=True)

    def on_modified(self, event):
        # Chỉ reload khi file .py được sửa
        if event.src_path.endswith(".py"):
            print(f"File changed: {event.src_path}. Reloading...")
            if self.process:
                self.process.kill()
                self.process.wait()  # Đợi tiến trình cũ kết thúc hẳn

            # Khởi động lại tiến trình
            self.start_process()


if __name__ == "__main__":
    path = "."
    # THAY ĐỔI DUY NHẤT: Trỏ đến file run.py của chúng ta
    command = "python run.py"

    print("Starting developer runner with auto-reload...")
    print(f"Watching for changes in: {os.path.abspath(path)}")
    print(f"Running command: '{command}'")

    event_handler = ReloadHandler(command)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping runner...")
        if event_handler.process:
            event_handler.process.kill()
        observer.stop()

    observer.join()
    print("Runner stopped.")
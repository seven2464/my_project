import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from global_store import shared_data

class Camera(QThread):
    frame_ready = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.capture = None
        self.isRunning = False

    def run(self):
        cameraNum = shared_data.get('cameraNum', '1')
        self.isRunning = True
        self.capture = cv2.VideoCapture(int(cameraNum),cv2.CAP_DSHOW)
        while self.isRunning:
            ret, frame = self.capture.read()
            if not ret:
                break
            self.frame_ready.emit(frame)

    def stop(self):
        self.isRunning = False
        if self.capture:
            self.capture.release()


import cv2 as cv
from ultralytics import YOLO
import threading
import time

class OnboardVision:

    def __init__(self, initialModelPath="", cameraIndex=0, targetObjects=None):
        self._cameraIndex = cameraIndex
        self._isRunning = False
        self._cap = None
        self._model = YOLO(initialModelPath)
        self._targetObjects = targetObjects if targetObjects is not None else []
        self._currentFrame = None
        self._frameLock = threading.Lock()

    @property
    def isRunning(self):
        return self._isRunning
        
    def cameraStart(self):
        self._isRunning = True
        threading.Thread(target=self._cameraLoop, daemon=True).start()

    def _cameraLoop(self):
        while self._isRunning:
            if self._cap is None or not self._cap.isOpened():
                self._cap = cv.VideoCapture(self._cameraIndex)
                time.sleep(1.0)
                continue
                
            success, frame = self._cap.read()
            if success:
                with self._frameLock:
                    self._currentFrame = frame.copy()
            
            else:
                self._cap.release()
                self._cap = None

            time.sleep(0.01)

    def detection(self):
        if not self._isRunning:
            return None, None

        with self._frameLock:
            if self._currentFrame is None:
                return None, None
            
            frame = self._currentFrame.copy()

        results = self._model(frame, conf=0.80, stream=True)
        detectionsData = []

        for r in results:
            for box in r.boxes:
                coords = box.xyxy[0].tolist()
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                name = self._model.names[cls]
                
                if name in self._targetObjects:
                    detectionsData.append({
                        "name": name, 
                        "bbox": coords, 
                        "conf": conf
                    })

        return detectionsData, frame

    def cameraStop(self):
        self._isRunning = False
        time.sleep(0.1)
        if self._cap is not None:
            self._cap.release()

        return "Camera Stopped"
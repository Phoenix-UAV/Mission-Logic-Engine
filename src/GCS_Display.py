import cv2 as cv

class GCSDisplay:

    def __init__(self):
        self._isRunning = False

    @property
    def isRunning(self):
        return self._isRunning

    def cameraStart(self):
        cv.namedWindow("YOLO Real-Time Detection", cv.WINDOW_GUI_NORMAL)
        self._isRunning = True
        return "Camera Started"

    def detection(self, frame, detectionsData):
        if not self._isRunning:
            return "[IDLE]"

        try:
            annotated_frame = frame.copy()

            if detectionsData:
                for item in detectionsData:
                    bbox = [int(coord) for coord in item["bbox"]]
                    cv.rectangle(annotated_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 0), 2)
                    
                    cv.putText(annotated_frame, f"{item['name']} {item['conf']:.2f}", 
                               (bbox[0], bbox[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

            cv.imshow("YOLO Real-Time Detection", annotated_frame)
            cv.waitKey(1)

            return "[OK]"

        except Exception:
            return "[Fatal Error]"

    def cameraStop(self):
        self._isRunning = False
        cv.destroyAllWindows()
        return "Camera Stopped"
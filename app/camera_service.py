import cv2
import numpy as np
import time

try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except Exception:
    PICAMERA_AVAILABLE = False


class CameraService:
    def __init__(self):
        self.camera = None
        self.last_frame = None

        if PICAMERA_AVAILABLE:
            self.camera = Picamera2()
            config = self.camera.create_preview_configuration(
                main={"size": (1920, 1080)}
            )
            self.camera.configure(config)
            self.camera.start()
            time.sleep(1)

    def get_frame(self):
        if self.camera:
            frame = self.camera.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        else:
            frame = self._mock_frame()

        self.last_frame = frame
        return frame

    def get_jpeg_frame(self):
        frame = self.get_frame()

        success, jpeg = cv2.imencode(".jpg", frame)

        if not success:
            return None

        return jpeg.tobytes()

    def capture_image(self):
        return self.get_frame()

    def _mock_frame(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(
            frame,
            "Camera not available",
            (130, 230),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )
        return frame


camera_service = CameraService()
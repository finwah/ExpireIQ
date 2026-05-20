import cv2
import numpy as np


class CameraService:
    def __init__(self):
        self.camera = None
        self.available = False
        self._start_camera()

    def _start_camera(self):
        try:
            from picamera2 import Picamera2

            self.camera = Picamera2()

            config = self.camera.create_preview_configuration(
                main={"size": (1280, 720), "format": "RGB888"}
            )

            self.camera.configure(config)
            self.camera.start()

            self.available = True
            print("Pi camera started successfully.")

        except Exception as e:
            self.available = False
            self.camera = None
            print("Camera not available:", e)

    def capture_image(self):
        if not self.available or self.camera is None:
            return self._fallback_frame()

        try:
            frame = self.camera.capture_array()

            if frame is None:
                return self._fallback_frame()

            return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        except Exception as e:
            print("Camera capture failed:", e)
            return self._fallback_frame()

    def get_jpeg_frame(self):
        frame = self.capture_image()

        success, buffer = cv2.imencode(".jpg", frame)

        if not success:
            return None

        return buffer.tobytes()

    def _fallback_frame(self):
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)

        cv2.rectangle(frame, (330, 270), (950, 450), (56, 189, 248), 4)
        cv2.putText(
            frame,
            "Camera not available",
            (360, 380),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (255, 255, 255),
            3,
            cv2.LINE_AA
        )

        return frame


camera_service = CameraService()
import cv2
import numpy as np
from pyzbar.pyzbar import decode


def detect_barcode(frame):
    if frame is None:
        return None

    attempts = build_barcode_attempts(frame)

    for image in attempts:
        decoded_codes = decode(image)

        if decoded_codes:
            return decoded_codes[0].data.decode("utf-8")

    return None


def build_barcode_attempts(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    height, width = gray.shape

    center_crop = gray[
        int(height * 0.18):int(height * 0.82),
        int(width * 0.10):int(width * 0.90)
    ]

    enlarged = cv2.resize(
        center_crop,
        None,
        fx=1.8,
        fy=1.8,
        interpolation=cv2.INTER_CUBIC
    )

    sharpen_kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])

    sharpened = cv2.filter2D(enlarged, -1, sharpen_kernel)

    _, otsu = cv2.threshold(
        sharpened,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    adaptive = cv2.adaptiveThreshold(
        sharpened,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        2
    )

    return [
        gray,
        center_crop,
        enlarged,
        sharpened,
        otsu,
        adaptive,
    ]
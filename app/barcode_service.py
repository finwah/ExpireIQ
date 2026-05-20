from pyzbar.pyzbar import decode
import cv2
import numpy as np


def detect_barcode(frame):
    if frame is None:
        return None

    processed_images = build_barcode_attempts(frame)

    for image in processed_images:
        decoded_codes = decode(image)

        if decoded_codes:
            return decoded_codes[0].data.decode("utf-8")

    return None


def build_barcode_attempts(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    enlarged = cv2.resize(
        gray,
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

    adaptive = cv2.adaptiveThreshold(
        sharpened,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        2
    )

    _, otsu = cv2.threshold(
        sharpened,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return [
        frame,
        gray,
        enlarged,
        sharpened,
        adaptive,
        otsu
    ]
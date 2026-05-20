import re
from datetime import datetime

import cv2
import pytesseract


DATE_PATTERNS = [
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2}\b",
    r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
    r"\b\d{1,2}\s?(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s?\d{2,4}\b"
]


def extract_expiry_date(frame):
    processed_images = preprocess_for_ocr(frame)

    best_text = ""

    for image in processed_images:
        text = pytesseract.image_to_string(image)

        if len(text.strip()) > len(best_text.strip()):
            best_text = text

        date_text = find_date_in_text(text)

        if date_text:
            parsed_date = normalise_date(date_text)

            if parsed_date:
                return {
                    "raw_text": text.strip(),
                    "date": parsed_date
                }

    return {
        "raw_text": best_text.strip(),
        "date": None
    }


def preprocess_for_ocr(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    enlarged = cv2.resize(gray, None, fx=2, fy=2)

    blurred = cv2.GaussianBlur(enlarged, (3, 3), 0)

    _, threshold = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    adaptive = cv2.adaptiveThreshold(
        enlarged,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        2
    )

    return [threshold, adaptive, enlarged]


def find_date_in_text(text):
    cleaned_text = text.lower()
    cleaned_text = cleaned_text.replace("best before", " ")
    cleaned_text = cleaned_text.replace("use by", " ")
    cleaned_text = cleaned_text.replace("expiry", " ")
    cleaned_text = cleaned_text.replace("expires", " ")
    cleaned_text = cleaned_text.replace("bbe", " ")

    for pattern in DATE_PATTERNS:
        match = re.search(pattern, cleaned_text, re.IGNORECASE)

        if match:
            return match.group(0)

    return None


def normalise_date(date_text):
    date_text = date_text.strip().replace(".", "/")

    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d/%m/%y",
        "%d-%m-%y",
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%d %b %Y",
        "%d %B %Y",
        "%d%b%Y",
        "%d%B%Y",
        "%d %b %y",
        "%d %B %y",
        "%d%b%y",
        "%d%B%y"
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(date_text, fmt)
            return parsed.date().isoformat()
        except ValueError:
            pass

    return None
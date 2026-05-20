import calendar
import re
from datetime import date, datetime

import cv2
import numpy as np
import pytesseract


OCR_CONFIG = (
    "--psm 7 "
    "-c tessedit_char_whitelist=0123456789/-.ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
)


DATE_PATTERNS = [
    r"\b\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4}\b",
    r"\b\d{4}[\/\-.]\d{1,2}[\/\-.]\d{1,2}\b",
    r"\b\d{1,2}[\/\-]\d{2,4}\b",
    r"\b\d{4}\b",
    r"\b\d{1,2}\s?(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s?\d{2,4}\b",
    r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s?\d{2,4}\b",
]


MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


def extract_expiry_date(frame):
    if frame is None:
        return {"raw_text": "", "date": None}

    processed_images = preprocess_for_ocr(frame)
    best_text = ""

    for image in processed_images:
        try:
            text = pytesseract.image_to_string(
                image,
                config=OCR_CONFIG,
                timeout=4
            )
        except RuntimeError:
            continue

        cleaned_text = clean_ocr_text(text)

        if len(cleaned_text) > len(best_text):
            best_text = cleaned_text

        date_text = find_date_in_text(cleaned_text)

        if date_text:
            parsed_date = normalise_date(date_text)

            if parsed_date:
                return {
                    "raw_text": cleaned_text,
                    "date": parsed_date
                }

    return {
        "raw_text": best_text,
        "date": None
    }


def preprocess_for_ocr(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    height, width = gray.shape

    crops = []

    # Large centre crop
    crops.append(gray[
        int(height * 0.15):int(height * 0.85),
        int(width * 0.08):int(width * 0.92)
    ])

    # Medium centre crop
    crops.append(gray[
        int(height * 0.25):int(height * 0.75),
        int(width * 0.15):int(width * 0.85)
    ])

    # Full grayscale fallback
    crops.append(gray)

    processed_images = []

    for crop in crops:
        enlarged = cv2.resize(
            crop,
            None,
            fx=1.6,
            fy=1.6,
            interpolation=cv2.INTER_CUBIC
        )

        sharpen_kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])

        sharpened = cv2.filter2D(enlarged, -1, sharpen_kernel)

        _, thresholded = cv2.threshold(
            sharpened,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        processed_images.append(sharpened)
        processed_images.append(thresholded)

    cv2.imwrite("debug_ocr_crop.jpg", processed_images[0])
    return processed_images[:4]


def clean_ocr_text(text):
    text = text.lower()

    replacements = {
        "best before": " ",
        "best-before": " ",
        "bestbefore": " ",
        "use by": " ",
        "use-by": " ",
        "expiry": " ",
        "expires": " ",
        "exp": " ",
        "bbe": " ",
        "bb": " ",
        "lot": " ",
        "batch": " ",
        "\\": "/",
        "_": "-",
        "o": "0",
        "l": "1",
        "i": "1",
        "|": "1",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_date_in_text(text):
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(0)

    return None


def normalise_date(date_text):
    date_text = date_text.strip().lower()
    date_text = date_text.replace(".", "/")
    date_text = re.sub(r"\s+", " ", date_text)

    parsers = [
        parse_full_numeric_date,
        parse_year_first_date,
        parse_month_year_date,
        parse_compact_month_year,
        parse_text_month_date,
    ]

    for parser in parsers:
        parsed = parser(date_text)

        if parsed:
            return parsed.isoformat()

    return None


def parse_full_numeric_date(date_text):
    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d/%m/%y",
        "%d-%m-%y",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%m/%d/%y",
        "%m-%d-%y",
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(date_text, fmt).date()

            if is_reasonable_expiry_date(parsed):
                return parsed

        except ValueError:
            continue

    return None


def parse_year_first_date(date_text):
    formats = [
        "%Y/%m/%d",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(date_text, fmt).date()

            if is_reasonable_expiry_date(parsed):
                return parsed

        except ValueError:
            continue

    return None


def parse_month_year_date(date_text):
    match = re.fullmatch(r"(\d{1,2})[\/\-](\d{2,4})", date_text)

    if not match:
        return None

    month = int(match.group(1))
    year = int(match.group(2))

    return build_month_year_date(month, year)


def parse_compact_month_year(date_text):
    match = re.fullmatch(r"(\d{2})(\d{2})", date_text)

    if not match:
        return None

    month = int(match.group(1))
    year = int(match.group(2))

    return build_month_year_date(month, year)


def parse_text_month_date(date_text):
    parts = date_text.replace("-", " ").replace("/", " ").split()

    if len(parts) == 2:
        month_text, year_text = parts

        month = MONTHS.get(month_text[:3])
        year = safe_int(year_text)

        if month and year:
            return build_month_year_date(month, year)

    if len(parts) == 3:
        day_text, month_text, year_text = parts

        day = safe_int(day_text)
        month = MONTHS.get(month_text[:3])
        year = safe_int(year_text)

        if day and month and year:
            if year < 100:
                year += 2000

            try:
                parsed = date(year, month, day)

                if is_reasonable_expiry_date(parsed):
                    return parsed

            except ValueError:
                return None

    return None


def build_month_year_date(month, year):
    if month < 1 or month > 12:
        return None

    if year < 100:
        year += 2000

    last_day = calendar.monthrange(year, month)[1]
    parsed = date(year, month, last_day)

    if is_reasonable_expiry_date(parsed):
        return parsed

    return None


def safe_int(value):
    try:
        return int(value)
    except ValueError:
        return None


def is_reasonable_expiry_date(parsed_date):
    today = date.today()
    max_year = today.year + 10

    return parsed_date >= today and parsed_date.year <= max_year
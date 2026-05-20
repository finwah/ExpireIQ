try:
    from pyzbar.pyzbar import decode
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False


def detect_barcode(frame):
    if not PYZBAR_AVAILABLE:
        print("pyzbar/zbar is not available on this machine.")
        return None

    barcodes = decode(frame)

    if not barcodes:
        return None

    barcode = barcodes[0].data.decode("utf-8")
    return barcode
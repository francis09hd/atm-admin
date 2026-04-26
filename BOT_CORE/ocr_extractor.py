import re

try:
    import uiautomator2 as u2
    _U2_OK = True
except Exception:
    _U2_OK = False

try:
    import easyocr
    _EASYOCR_OK = True
except Exception:
    _EASYOCR_OK = False


def extract_distance_and_zone(device_ip="127.0.0.1:62001"):
    """Extrae distancia y zona desde la pantalla del dispositivo vía OCR.
    Retorna (None, None) si easyocr o uiautomator2 no están disponibles."""
    if not _U2_OK or not _EASYOCR_OK:
        return None, None
    try:
        d = u2.connect(device_ip)
        img = d.screenshot(format='opencv')
        reader = easyocr.Reader(['es', 'en'])
        result = reader.readtext(img)
        distancia = None
        zona = None
        for _, text, _ in result:
            dist_match = re.search(r"(\d+[\.,]?\d*)\s*km", text, re.I)
            zona_match = re.search(r"zona[:\s]+([\w\s]+)", text, re.I)
            if dist_match:
                distancia = float(dist_match.group(1).replace(",", "."))
            if zona_match:
                zona = zona_match.group(1).strip()
        return distancia, zona
    except Exception:
        return None, None

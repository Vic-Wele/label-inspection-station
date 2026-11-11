"""Find the label card in a grayscale image and crop around it (locate, then inspect)."""
import cv2

KERNEL = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
MIN_AREA = 200_000   # a card is about 1000 x 850 px; ignore small bright things like tape
MIN_BRIGHTNESS = 120 # a white card; the dark box top is about 40 to 60
MARGIN = 0.05        # keep 5% extra around the card


def locate_card(gray):
    """Return (x, y, w, h) of the card, or None if no card is found."""
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    card = max(contours, key=cv2.contourArea)
    if cv2.contourArea(card) < MIN_AREA:
        return None
    x, y, w, h = cv2.boundingRect(card)
    if gray[y:y + h, x:x + w].mean() < MIN_BRIGHTNESS:
        return None
    return x, y, w, h


def card_crop(gray):
    """Crop around the card with a small margin, or return None if there's no card."""
    box = locate_card(gray)
    if box is None:
        return None
    x, y, w, h = box
    mx, my = int(w * MARGIN), int(h * MARGIN)
    H, W = gray.shape
    return gray[max(0, y - my):min(H, y + h + my), max(0, x - mx):min(W, x + w + mx)]
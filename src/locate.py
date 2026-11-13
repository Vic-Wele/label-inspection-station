"""Find the label card in a grayscale image, measure its tilt, straighten it, and crop around it."""
import cv2

KERNEL = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
MIN_AREA = 200_000   # a card is about 1000 x 850 px; ignore small bright things like tape
MIN_BRIGHTNESS = 120 # a white card; the dark box top is about 40 to 60
MARGIN = 0.05        # keep 5% extra around the card


def find_card_contour(gray):
    """Return the card's outline, or None if no card is found."""
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
    return card


def tilt(contour):
    """Tilt of a contour in degrees, -45 to +45 (0 = level)."""
    return ((cv2.minAreaRect(contour)[2] + 45) % 90) - 45


def locate_card(gray):
    """Return (x, y, w, h) of the card, or None if no card is found."""
    card = find_card_contour(gray)
    return None if card is None else cv2.boundingRect(card)


def card_angle(gray):
    """Return the card's tilt in degrees, or None if no card."""
    card = find_card_contour(gray)
    return None if card is None else tilt(card)


def crop_box(gray, contour):
    x, y, w, h = cv2.boundingRect(contour)
    mx, my = int(w * MARGIN), int(h * MARGIN)
    H, W = gray.shape
    return gray[max(0, y - my):min(H, y + h + my), max(0, x - mx):min(W, x + w + mx)]


def straight_crop(gray):
    """Straighten the card and crop around it. Returns (crop, tilt_degrees), or (None, None) if no card."""
    card = find_card_contour(gray)
    if card is None:
        return None, None
    angle = tilt(card)
    if abs(angle) < 0.1:
        return crop_box(gray, card), angle
    (cx, cy), _, _ = cv2.minAreaRect(card)
    H, W = gray.shape
    best = None
    for sign in (1, -1):  # try both rotation directions, keep the one that ends up level
        M = cv2.getRotationMatrix2D((cx, cy), sign * angle, 1.0)
        rotated = cv2.warpAffine(gray, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        c2 = find_card_contour(rotated)
        if c2 is not None and (best is None or abs(tilt(c2)) < best[0]):
            best = (abs(tilt(c2)), rotated, c2)
    if best is None:
        return crop_box(gray, card), angle
    return crop_box(best[1], best[2]), angle


def card_crop(gray):
    """Straightened crop around the card, or None if there's no card."""
    return straight_crop(gray)[0]
"""Generate shipping labels on Avery 15264 sheets (US Letter, 6 per sheet, 4 x 3.333 in)."""
import csv
from pathlib import Path

from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont

DPI = 300
PAGE_W, PAGE_H = int(8.5 * DPI), int(11 * DPI)   # 2550 x 3300 px
LABEL_W, LABEL_H = 4 * DPI, 1000                  # 4 x 3.333 in
LEFT, GAP_X, TOP = 47, 56, 150                    # Avery 15264 margins in px
OUT_DIR = Path("labels")


def font(size, bold=False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(name, size)


def make_barcode(text):
    options = {"module_width": 5 * 25.4 / DPI, "module_height": 25.0,
               "quiet_zone": 6.5, "write_text": False, "dpi": DPI}
    return Code128(text, writer=ImageWriter()).render(options).convert("L")


def make_label(label_id, lot):
    img = Image.new("L", (LABEL_W, LABEL_H), 255)
    d = ImageDraw.Draw(img)
    d.rectangle([30, 30, LABEL_W - 31, LABEL_H - 31], outline=0, width=6)
    d.text((70, 60), "DEMO LOGISTICS", font=font(60, bold=True), fill=0)
    d.text((70, 140), "SHIP TO: Station 01, Line A", font=font(36), fill=0)
    bc = make_barcode(label_id)
    bx = (LABEL_W - bc.width) // 2
    img.paste(bc, (bx, 230))
    d.text((LABEL_W // 2, 230 + bc.height + 15), label_id,
           font=font(48, bold=True), fill=0, anchor="mt")
    d.text((70, 660), f"ORDER: ORD-{label_id[-4:]}", font=font(40), fill=0)
    d.text((70, 720), "DEST: DOCK 3", font=font(40), fill=0)
    d.text((70, LABEL_H - 120), f"LOT {lot}", font=font(40), fill=0)
    d.text((LABEL_W - 70, LABEL_H - 120), "WT 1.2 KG", font=font(40), fill=0, anchor="ra")
    return img, (bx, 230, bx + bc.width, 230 + bc.height)


def fade(img):
    return img.point(lambda p: int(255 - (255 - p) * 0.5))


def break_barcode(img, box):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    for frac in (0.30, 0.55, 0.80):
        x = x0 + int((x1 - x0) * frac)
        d.rectangle([x, y0, x + 25, y1], fill=255)
    return img


def main():
    OUT_DIR.mkdir(exist_ok=True)
    plan = []
    for i in range(1, 31):
        label_id = f"PKG-{i:04d}"
        if i <= 19:
            kind, note = "good", "print normally"
        elif i <= 26:
            kind, note = "good_for_hand_defect", "tear (20-22), smudge (23-24), scratch barcode (25-26)"
        elif i <= 28:
            kind, note = "faded", "printed faded"
        else:
            kind, note = "damaged_barcode", "printed with gaps in bars"
        plan.append((label_id, kind, note))

    pages, rows = [], []
    for n, (label_id, kind, note) in enumerate(plan):
        if n % 6 == 0:
            page = Image.new("L", (PAGE_W, PAGE_H), 255)
            pages.append(page)
        lot = f"2610-{'ABCDE'[n % 5]}"
        img, bc_box = make_label(label_id, lot)
        if kind == "faded":
            img = fade(img)
        if kind == "damaged_barcode":
            img = break_barcode(img, bc_box)
        col, row = (n % 6) % 2, (n % 6) // 2
        x = LEFT + col * (LABEL_W + GAP_X)
        y = TOP + row * LABEL_H
        pages[-1].paste(img, (x, y))
        rows.append([label_id, kind, lot, len(pages), (n % 6) + 1, note])

    pdf_path = OUT_DIR / "labels_avery15264.pdf"
    pages[0].save(pdf_path, save_all=True, append_images=pages[1:], resolution=DPI)
    with open(OUT_DIR / "manifest.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["label_id", "intended_class", "lot", "sheet", "position", "note"])
        w.writerows(rows)
    print(f"Saved {pdf_path} ({len(pages)} sheets) and {OUT_DIR / 'manifest.csv'} ({len(rows)} labels)")


if __name__ == "__main__":
    main()

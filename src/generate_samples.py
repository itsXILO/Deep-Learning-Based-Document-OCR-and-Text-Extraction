import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "input"
FONT_PATH = r"C:\Windows\Fonts\arial.ttf"
PAGE_SIZE = (1200, 1500)
MARGIN = 80


def _font(size):
    return ImageFont.truetype(FONT_PATH, size)


def _wrap(draw, text, font, max_width):
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        lines.extend(textwrap.wrap(paragraph, width=max_width // 8))
    return lines


def render_document(filename, title, paragraphs, item_lines=None):
    image = Image.new("RGB", PAGE_SIZE, "white")
    draw = ImageDraw.Draw(image)
    y = MARGIN
    title_font = _font(44)
    body_font = _font(28)
    mono_font = _font(26)

    draw.text((MARGIN, y), title, fill="black", font=title_font)
    y += 110
    draw.line((MARGIN, y, PAGE_SIZE[0] - MARGIN, y), fill="black", width=2)
    y += 50

    for paragraph in paragraphs:
        for line in _wrap(draw, paragraph, body_font, PAGE_SIZE[0] - 2 * MARGIN):
            draw.text((MARGIN, y), line, fill="black", font=body_font)
            y += 46
        y += 26

    if item_lines:
        y += 40
        draw.text((MARGIN, y), "ITEMS", fill="black", font=title_font)
        y += 70
        for line in item_lines:
            draw.text((MARGIN, y), line, fill="black", font=mono_font)
            y += 42
        y += 20
        draw.line((MARGIN, y, PAGE_SIZE[0] - MARGIN, y), fill="black", width=1)
        y += 44
        draw.text((MARGIN, y), "TOTAL: $1,274.50", fill="black", font=mono_font)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT_DIR / filename)
    print("wrote", OUTPUT_DIR / filename)


def main():
    render_document(
        "sample1_letter.png",
        "Acme Cleaning Services",
        [
            "Dear Resident, We will be performing routine cleaning of the main lobby",
            "and hallways this Friday from 9 AM to 12 PM. Please remove personal",
            "belongings from common areas beforehand. We appreciate your patience.",
        ],
    )
    render_document(
        "sample2_invoice.png",
        "Bright Ideas Invoice #4821",
        [
            "Invoice Date: March 4, 2026 due on April 3, 2026. Payment by bank",
            "transfer to account number 1200-5567-9081 referenced with this number.",
        ],
        [
            "1   Conference table lamp      x2   $120.00",
            "2   Desk organizer             x1    $45.50",
            "3   Ergonomic chair            x3   $960.00",
            "4   Cable management kit       x6    $49.00",
        ],
    )
    render_document(
        "sample3_notes.png",
        "Team Meeting Notes",
        [
            "We discussed the OCR pipeline rollout. The preprocessing step should",
            "improve accuracy on scanned documents. Next week we compare results",
            "against the baseline and update the documentation with run instructions.",
        ],
    )


if __name__ == "__main__":
    main()
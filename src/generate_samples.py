import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "input"
FONT_PATH = r"C:\Windows\Fonts\arial.ttf"
PAGE_SIZE = (1200, 1500)
MARGIN = 80


def _font(size):
    return ImageFont.truetype(FONT_PATH, size)


def _font_bold(size):
    return ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", size)


def _wrap_by_pixels(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _wrap(draw, text, font, max_width):
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        lines.extend(textwrap.wrap(paragraph, width=max_width // 8))
    return lines


def render_document(
    filename,
    title,
    paragraphs,
    item_lines=None,
    item_heading="ITEMS",
    total_line="TOTAL: $1,274.50",
    page_size=PAGE_SIZE,
    title_size=44,
    body_size=28,
    mono_size=26,
    line_gap=46,
    outline=True,
):
    image = Image.new("RGB", page_size, "white")
    draw = ImageDraw.Draw(image)
    y = MARGIN
    title_font = _font_bold(title_size)
    body_font = _font(body_size)
    mono_font = _font(mono_size)

    draw.text((MARGIN, y), title, fill="black", font=title_font)
    y += int(title_size * 2.5)
    if outline:
        draw.line((MARGIN, y, page_size[0] - MARGIN, y), fill="black", width=2)
    y += 50

    for paragraph in paragraphs:
        for line in _wrap(draw, paragraph, body_font, page_size[0] - 2 * MARGIN):
            draw.text((MARGIN, y), line, fill="black", font=body_font)
            y += line_gap
        y += 26

    if item_lines:
        y += 40
        draw.text((MARGIN, y), item_heading, fill="black", font=_font_bold(title_size))
        y += title_size * 2
        for line in item_lines:
            draw.text((MARGIN, y), line, fill="black", font=mono_font)
            y += int(mono_size * 1.6)
        y += 20
        draw.line((MARGIN, y, page_size[0] - MARGIN, y), fill="black", width=1)
        y += 44
        draw.text((MARGIN, y), total_line, fill="black", font=_font_bold(mono_size))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT_DIR / filename)
    print("wrote", OUTPUT_DIR / filename)


def render_card(filename, bold_word, definition_lines):
    image = Image.new("RGB", (900, 450), "white")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((20, 20, 880, 430), radius=18, outline=(30, 120, 200), width=6)
    draw.text((70, 90), bold_word, fill="black", font=_font_bold(56))
    draw.line((70, 210, 830, 210), fill=(30, 120, 200), width=3)
    y = 250
    body_font = _font(30)
    for line in _wrap_by_pixels(draw, " ".join(definition_lines), body_font, 760):
        draw.text((70, y), line, fill="black", font=body_font)
        y += 44

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
    render_document(
        "sample4_receipt.png",
        "City Cafe",
        [
            "Thank you for your visit! Have a great day.",
        ],
        item_heading="YOUR RECEIPT",
        total_line="TOTAL: $18.50",
        item_lines=[
            "1   Cappuccino             $4.50",
            "2   Butter croissant       $3.50",
            "1   Club sandwich         $9.50",
            "1   Orange juice           $1.00",
        ],
    )
    render_document(
        "sample5_notice.png",
        "Community Notice",
        [
            "Fall Festival this Saturday from 10 AM to 4 PM in the",
            "main park. Free admission, food stalls, and live music.",
            "Rain date is the following Sunday. Hope to see you there!",
        ],
    )
    render_document(
        "sample6_flight.png",
        "Flight Confirmation",
        [
            "Passenger: Jane Smith   Flight: UA 1287",
            "From: New York (JFK)    To: Chicago (ORD)",
            "Depart: 9:45 AM    Arrive: 11:20 AM    Seat: 14B",
        ],
    )
    render_card(
        "sample7_card.png",
        "Ocr",
        ["Optical character recognition is the technology",
         "that turns images of text into editable text."],
    )


if __name__ == "__main__":
    main()
import re
from config import OcrConfig


def filter_low_confidence(records, min_confidence: float):
    return [r for r in records if r["confidence"] >= min_confidence]


def _bbox_midpoint(record):
    xs = [p[0] for p in record["bbox"]]
    ys = [p[1] for p in record["bbox"]]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def _bbox_height(record):
    ys = [p[1] for p in record["bbox"]]
    return max(ys) - min(ys)


def sort_records(records):
    if not records:
        return []
    heights = sorted(_bbox_height(r) for r in records)
    median_height = heights[len(heights) // 2]
    row_gap = max(median_height * 0.6, 8.0)

    rows = []
    remaining = sorted(records, key=lambda r: _bbox_midpoint(r)[1])
    for record in remaining:
        _, y = _bbox_midpoint(record)
        placed = False
        for row in rows:
            anchor = sum(_bbox_midpoint(r)[1] for r in row) / len(row)
            if abs(y - anchor) <= row_gap:
                row.append(record)
                placed = True
                break
        if not placed:
            rows.append([record])

    ordered = []
    for row in sorted(rows, key=lambda r: _bbox_midpoint(r[0])[1]):
        ordered.extend(sorted(row, key=lambda r: _bbox_midpoint(r)[0]))
    return ordered


def group_into_paragraphs(records):
    if not records:
        return []
    heights = sorted(_bbox_height(r) for r in records)
    median_height = heights[len(heights) // 2]
    gap_threshold = max(median_height * 1.4, 12.0)

    paragraphs = []
    current = [records[0]]
    prev = records[0]
    for record in records[1:]:
        prev_top = min(p[1] for p in prev["bbox"])
        prev_bottom = max(p[1] for p in prev["bbox"])
        curr_top = min(p[1] for p in record["bbox"])
        if curr_top - prev_bottom > gap_threshold:
            paragraphs.append(current)
            current = []
        current.append(record)
        prev = record
    paragraphs.append(current)
    return paragraphs


def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text


def records_to_text(paragraphs) -> str:
    chunks = []
    for paragraph in paragraphs:
        lines = [clean_text(record["text"]) for record in paragraph]
        lines = [line for line in lines if line]
        if lines:
            chunks.append("\n".join(lines))
    return "\n\n".join(chunks)


def postprocess(records, config: OcrConfig):
    kept = filter_low_confidence(records, config.min_confidence)
    ordered = sort_records(kept)
    paragraphs = group_into_paragraphs(ordered)
    text = records_to_text(paragraphs)
    return {"ordered_records": ordered, "paragraphs": paragraphs, "text": text}
import argparse
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

import cv2
import numpy as np

from config import DATA_INPUT_DIR, DATA_OUTPUT_DIR
from src.pipeline import IMAGE_EXTS


def word_tokens(text: str):
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).split()


def word_accuracy(reference: str, hypothesis: str) -> float:
    ref = word_tokens(reference)
    hyp = word_tokens(hypothesis)
    if not ref:
        return 1.0 if not hyp else 0.0
    matcher = SequenceMatcher(None, ref, hyp)
    matched = sum(block.size for block in matcher.get_matching_blocks())
    return matched / len(ref)


def draw_boxes(image_path, json_path, out_path):
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")
    with open(json_path, encoding="utf-8") as handle:
        data = json.load(handle)
    for line in data["lines"]:
        points = np.array(line["bbox"], dtype=np.int32)
        cv2.polylines(image, [points], isClosed=True, color=(0, 200, 0), thickness=2)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), image)


def evaluate(input_dir, output_dir, truth_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    truth_dir = Path(truth_dir)

    total_acc = 0.0
    total_file = 0
    rows = []
    for image_path in sorted(input_dir.iterdir()):
        if image_path.suffix.lower() not in IMAGE_EXTS:
            continue
        image_path = Path(image_path)
        json_path = output_dir / f"{image_path.stem}.json"
        truth_path = truth_dir / f"{image_path.stem}.txt"
        if not json_path.exists() or not truth_path.exists():
            continue
        hypothesis = json.loads(json_path.read_text(encoding="utf-8"))["text"]
        reference = truth_path.read_text(encoding="utf-8")
        acc = word_accuracy(reference, hypothesis)
        boxes_path = output_dir / "boxes" / f"{image_path.stem}_boxes.png"
        draw_boxes(image_path, json_path, boxes_path)
        rows.append((image_path.name, acc, boxes_path))
        total_acc += acc
        total_file += 1

    for name, acc, boxes_path in rows:
        print(f"{name}: word accuracy {acc:.2%}  (boxes: {boxes_path})")
    if total_file:
        print(f"\nMean word accuracy: {total_acc / total_file:.2%} over {total_file} documents")
    return rows


def main():
    parser = argparse.ArgumentParser(description="Evaluate OCR output against ground truth and draw boxes")
    parser.add_argument("--input", default=str(DATA_INPUT_DIR))
    parser.add_argument("--output", default=str(DATA_OUTPUT_DIR))
    parser.add_argument("--truth", default=str(DATA_INPUT_DIR.parent / "ground_truth"))
    args = parser.parse_args()
    evaluate(args.input, args.output, args.truth)


if __name__ == "__main__":
    main()
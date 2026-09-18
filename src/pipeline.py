import json
from pathlib import Path

import cv2

from config import PipelineConfig
from src.postprocessing import postprocess
from src.preprocessing import preprocess_image
from src.recognition import recognize

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def process_image(image_path, config: PipelineConfig, output_dir: Path):
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    processed = preprocess_image(image_path, config.preprocessing)
    records = recognize(processed, config.ocr)
    result = postprocess(records, config.ocr)

    stem = image_path.stem
    txt_path = output_dir / f"{stem}.txt"
    json_path = output_dir / f"{stem}.json"

    txt_path.write_text(result["text"], encoding="utf-8")
    payload = {
        "image": image_path.name,
        "text": result["text"],
        "lines": [
            {
                "text": record["text"],
                "confidence": record["confidence"],
                "bbox": record["bbox"],
            }
            for record in result["ordered_records"]
        ],
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    preprocessed_path = output_dir / f"{stem}_preprocessed.png"
    cv2.imwrite(str(preprocessed_path), processed)

    return payload


def process_folder(input_dir, output_dir, config: PipelineConfig):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    results = []
    for image_path in sorted(input_dir.iterdir()):
        if image_path.suffix.lower() not in IMAGE_EXTS:
            continue
        try:
            payload = process_image(image_path, config, output_dir)
            results.append({"path": str(image_path), "payload": payload})
            print(f"OK   {image_path.name}: {len(payload['lines'])} lines")
        except Exception as exc:
            print(f"FAIL {image_path.name}: {exc}")
    return results
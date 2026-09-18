import numpy as np
from config import OcrConfig


_reader = None


def _get_reader(config: OcrConfig):
    global _reader
    if _reader is None:
        _reader = __import__("easyocr").Reader(config.languages, gpu=config.use_gpu, verbose=False)
    return _reader


def recognize(image: np.ndarray, config: OcrConfig):
    reader = _get_reader(config)
    results = reader.readtext(image, paragraph=config.paragraph)
    records = []
    for bbox, text, confidence in results:
        records.append(
            {
                "bbox": [[int(x), int(y)] for x, y in bbox],
                "text": text,
                "confidence": round(float(confidence), 4),
            }
        )
    return records
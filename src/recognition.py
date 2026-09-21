import numpy as np
from config import OcrConfig


_readers = {}


def _get_reader(config: OcrConfig):
    key = (tuple(config.languages), bool(config.use_gpu))
    if key not in _readers:
        _readers[key] = __import__("easyocr").Reader(
            config.languages, gpu=config.use_gpu, verbose=False
        )
    return _readers[key]


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
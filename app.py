import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from config import DATA_INPUT_DIR, DATA_OUTPUT_DIR, OcrConfig, PipelineConfig, PreprocessingConfig
from src.pipeline import IMAGE_EXTS, process_folder, process_image

PROJECT_ROOT = Path(__file__).resolve().parent
WEB_DIR = PROJECT_ROOT / "static"
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output" / "web"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024


def _to_bool(value):
    return str(value or "").lower() in ("1", "true", "yes", "on")


def _pipeline_config(form):
    languages = [
        lang.strip()
        for lang in form.get("languages", "en").split(",")
        if lang.strip()
    ] or ["en"]
    use_gpu = _to_bool(form.get("use_gpu", "true"))
    preprocessing = PreprocessingConfig(deskew=_to_bool(form.get("deskew", "true")))
    ocr = OcrConfig(
        languages=languages,
        use_gpu=use_gpu,
        min_confidence=float(form.get("min_confidence", 0.4) or 0.4),
    )
    return PipelineConfig(preprocessing=preprocessing, ocr=ocr)


def _entry(file_name, payload, error=None):
    entry = {"file": file_name, "success": error is None}
    if error:
        entry["error"] = str(error)
        return entry
    processed = OUTPUT_DIR / f"{Path(payload['image']).stem}_preprocessed.png"
    payload = {
        "image": file_name,
        "text": payload["text"],
        "lines": payload["lines"],
        "preprocessed_url": f"/media/{processed.name}",
    }
    entry["payload"] = payload
    return entry


def _folder_entry(path, payload, error=None):
    entry = {"file": path.name, "success": error is None}
    if error:
        entry["error"] = str(error)
        return entry
    processed = OUTPUT_DIR / f"{Path(payload['image']).stem}_preprocessed.png"
    payload = {
        "image": path.name,
        "text": payload["text"],
        "lines": payload["lines"],
        "preprocessed_url": f"/media/{processed.name}",
        "original_url": f"/input-media/{path.name}",
    }
    entry["payload"] = payload
    return entry


@app.route("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(WEB_DIR, filename)


@app.route("/media/<path:filename>")
def media_files(filename):
    return send_from_directory(OUTPUT_DIR, filename)


@app.route("/input-media/<path:filename>")
def input_media_files(filename):
    return send_from_directory(DATA_INPUT_DIR, filename)


@app.post("/api/ocr")
def api_ocr():
    files = request.files.getlist("images")
    files = [f for f in files if f and f.filename]
    if not files:
        return jsonify({"error": "No images uploaded"}), 400

    config = _pipeline_config(request.form)
    results = []
    for file in files:
        suffix = Path(file.filename).suffix.lower()
        if suffix not in IMAGE_EXTS:
            results.append(_entry(file.filename, None, f"Unsupported type: {suffix}"))
            continue
        path = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"
        file.save(path)
        try:
            payload = process_image(path, config, OUTPUT_DIR)
            results.append(_entry(file.filename, payload))
        except Exception as exc:
            results.append(_entry(file.filename, None, exc))
        finally:
            path.unlink(missing_ok=True)
    return jsonify({"results": results, "config": {
        "languages": config.ocr.languages,
        "min_confidence": config.ocr.min_confidence,
        "deskew": config.preprocessing.deskew,
        "use_gpu": config.ocr.use_gpu,
    }})


@app.post("/api/process-folder")
def api_process_folder():
    config = _pipeline_config(request.form)
    results = []
    for image_path in sorted(DATA_INPUT_DIR.iterdir()):
        if image_path.suffix.lower() not in IMAGE_EXTS:
            continue
        try:
            payload = process_image(image_path, config, OUTPUT_DIR)
            results.append(_folder_entry(image_path, payload))
        except Exception as exc:
            results.append(_folder_entry(image_path, None, exc))
    return jsonify({"results": results})


if __name__ == "__main__":
    print(f"\n  OCR Studio -> http://127.0.0.1:5000")
    print(f"  Input folder: {DATA_INPUT_DIR}")
    print(f"  Output folder: {OUTPUT_DIR}\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
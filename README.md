# OCR Pipeline (EasyOCR + OpenCV)

Extracts text from document images using EasyOCR on the GPU with an OpenCV
preprocessing stage, and writes per-image text + JSON output.

## Features

- Preprocessing: grayscale, denoise, CLAHE contrast, width-resize, optional deskew (`src/preprocessing.py`)
- Recognition: EasyOCR (English, GPU) returning text, confidence, and bounding boxes (`src/recognition.py`)
- Post-processing: drops low-confidence lines, sorts top→bottom / left→right, reconstructs paragraphs (`src/postprocessing.py`)
- Pipeline + CLI: one command turns an image folder into per-image `.txt` + `.json` + preprocessed image (`src/pipeline.py`, `main.py`)
- Evaluation: word-level accuracy vs ground truth + detected-box overlay images (`evaluate.py`)

## Environment

- Windows, Python 3.12, CUDA-enabled GPU (RTX tested)
- Venv: `.venv` (see `requirements.txt` for exact pinned versions)

> `torch` is a CUDA build (`2.11.0+cu128`) from the PyTorch index — its runtime
> DLLs are self-contained. Recreate it with:
> pip install torch==2.11.0+cu128 --index-url https://download.pytorch.org/whl/cu128

## Quick start

```bash
.venv\Scripts\activate

# GPU sanity check
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"

# 1) Generate sample printed documents (optional)
python -m src.generate_samples

# 2) Run the pipeline on data/input -> data/output
python main.py

# Options: --no-gpu, --min-confidence 0.5, --no-deskew, --languages "en,fr"
python main.py --input data/input --output data/output

# 3) Evaluate vs ground truth + draw detection boxes
python evaluate.py --truth data/ground_truth
```

## Web UI (OCR Studio)

A Flask web app (`.venv`):

```bash
.venv\Scripts\activate
python app.py
# open http://127.0.0.1:5000
```

- Drag & drop or browse to **upload any image** and OCR it right away
- Options: min confidence, languages (en/fr/es/de/…), deskew, GPU toggle
- Results show the detected text, per-line confidence, and bounding-box
  overlay (hover a box to inspect that line), plus copy / download-as-.txt
- "Process input folder" runs the same pipeline over `data/input`
- Uploads are processed via `POST /api/ocr`; results land in `data/output/web`

> The EasyOCR reader is cached per language/GPU combo, so you can switch
> options between requests without reloading models.

## Outputs

`data/output/<name>.txt` — OCR text (paragraphs)
`data/output/<name>.json` — lines: text, confidence, bbox
`data/output/<name>_preprocessed.png` — processed image
`data/output/boxes/<name>_boxes.png` — detected regions (from `evaluate.py`)

## Sample results

Mean word accuracy on the bundled samples: ~97%.
# OCR Pipeline Project Documentation Guide

## 1. Executive Summary

This project is a document OCR pipeline built for images of printed text. It uses OpenCV for image preprocessing, EasyOCR for text recognition on the GPU, and custom post-processing to produce readable text files and structured JSON output per image.

The repository is designed to turn a folder of document images into:

- cleaned preprocessed images,
- OCR text output,
- per-line bounding box data,
- evaluation overlays and accuracy metrics against ground truth.

It is suitable for reports, slide decks, and book chapters because it has a clear end-to-end story: problem, method, implementation, evaluation, and limitations.

## 2. Project Goal

The goal is to extract accurate text from document-style images while improving recognition quality through preprocessing and organizing the OCR results into human-readable paragraphs.

The project focuses on three practical goals:

1. improve OCR accuracy on scanned or rendered documents,
2. keep the pipeline fast by using GPU-backed inference,
3. preserve structure by outputting both plain text and JSON line records.

## 3. What The System Does

The current implementation performs the following:

- reads images from `data/input/`,
- converts them to grayscale,
- denoises and enhances contrast,
- resizes them to a consistent width,
- optionally deskews them,
- runs EasyOCR with CUDA enabled,
- filters and orders OCR detections,
- rebuilds paragraphs,
- writes `.txt`, `.json`, and preprocessed image outputs,
- compares results against ground truth labels,
- draws detected text boxes for visual inspection.

## 4. Repository Structure

The important files and folders are:

- `main.py` - command-line entry point for OCR processing,
- `evaluate.py` - accuracy evaluation and box rendering,
- `config.py` - dataclasses for preprocessing, OCR, and pipeline settings,
- `src/preprocessing.py` - image cleaning and normalization,
- `src/recognition.py` - EasyOCR reader wrapper,
- `src/postprocessing.py` - ordering, grouping, and text cleanup,
- `src/pipeline.py` - orchestration of the full image-to-text flow,
- `src/generate_samples.py` - creates the bundled demo images,
- `data/input/` - source images,
- `data/output/` - OCR results and evaluation overlays,
- `data/ground_truth/` - reference text for evaluation,
- `requirements.txt` - pinned runtime dependencies.

## 5. End-To-End Pipeline

The OCR flow works in this order:

1. Load an image from disk.
2. Convert it to grayscale.
3. Denoise the image with non-local means filtering.
4. Apply CLAHE contrast enhancement.
5. Resize to a target width of 1600 pixels.
6. Deskew the image when enabled.
7. Run EasyOCR on the processed image using the GPU when available.
8. Convert OCR detections to a structured record format.
9. Filter out low-confidence results.
10. Sort detections top-to-bottom and left-to-right.
11. Group lines into paragraphs using vertical spacing.
12. Reconstruct cleaned paragraph text.
13. Write `.txt`, `.json`, and `_preprocessed.png` outputs.

This design is important for a presentation because it shows that OCR is not just a recognition step; it is a full document understanding pipeline.

## 6. Component Breakdown

### 6.1 Preprocessing

`src/preprocessing.py` contains the image improvement steps.

Key behaviors:

- grayscale conversion removes color noise,
- denoising reduces background texture and scan artifacts,
- CLAHE improves local contrast,
- resizing normalizes scale for OCR,
- deskewing corrects rotation when needed.

Why it matters:

- OCR models generally perform better on cleaner, consistently scaled images,
- deskewing improves detection on scanned pages,
- contrast enhancement helps faint text become readable.

### 6.2 Recognition

`src/recognition.py` wraps EasyOCR.

Key behaviors:

- the reader is created lazily and reused,
- it uses English by default,
- it can run with `gpu=True`,
- it returns bounding boxes, text, and confidence values.

The environment was verified with CUDA enabled, and the reader initializes on `cuda` rather than CPU.

### 6.3 Post-Processing

`src/postprocessing.py` turns raw OCR detections into readable output.

Key behaviors:

- drops records below a confidence threshold,
- groups nearby text into rows,
- orders rows top-to-bottom,
- orders text left-to-right within each row,
- merges lines into paragraphs based on vertical spacing,
- removes extra whitespace and punctuation spacing artifacts.

This stage is essential because OCR output is often accurate at the word level but still awkward to read if the spatial order is not reconstructed.

### 6.4 Pipeline Orchestration

`src/pipeline.py` coordinates the process for single images and folders.

Outputs per image:

- `<name>.txt` - reconstructed OCR text,
- `<name>.json` - structured OCR output with line text, confidence, and bounding boxes,
- `<name>_preprocessed.png` - processed image used for recognition.

### 6.5 Evaluation

`evaluate.py` compares OCR output to ground truth and draws detection overlays.

It computes a word-level accuracy score using token sequence matching and saves box visualization images under `data/output/boxes/`.

### 6.6 Sample Generation

`src/generate_samples.py` creates three synthetic document images:

- a letter,
- an invoice,
- meeting notes.

This gives the project a reproducible demo dataset and makes the workflow easier to explain in a report or chapter.

## 7. Configuration And Runtime

The runtime configuration is defined in `config.py`.

Defaults currently used by the pipeline:

- preprocessing target width: 1600,
- CLAHE clip limit: 2.0,
- denoise strength: 10.0,
- deskew: enabled,
- OCR language: English,
- OCR GPU: enabled unless `--no-gpu` is set,
- minimum confidence: 0.4 unless overridden.

The project was verified on Windows with Python 3.12 and a CUDA-capable NVIDIA GPU.

## 8. Verified Environment Notes

The environment was checked before documentation was written:

- `torch` is installed as `2.11.0+cu128`,
- `torch.cuda.is_available()` returned `True`,
- `easyocr.Reader(['en'], gpu=True)` initializes on `cuda`,
- the EasyOCR model cache was warmed locally,
- the OCR pipeline ran end-to-end on the bundled sample images.

## 9. Verified Results

The bundled sample set was processed successfully.

Observed evaluation results:

- `sample1_letter.png` - 100.00% word accuracy,
- `sample2_invoice.png` - 91.53% word accuracy,
- `sample3_notes.png` - 100.00% word accuracy,
- mean word accuracy - 97.18% over 3 documents.

These numbers are good material for a report or presentation because they show both strong performance and a realistic lower-performing case.

## 10. How To Run The Project

Typical commands from the repository root:

```bash
.venv\\Scripts\\activate
python main.py
python evaluate.py --truth data/ground_truth
```

Useful options:

- `--no-gpu` to force CPU inference,
- `--min-confidence <value>` to adjust filtering,
- `--no-deskew` to disable rotation correction,
- `--languages "en,fr"` to expand OCR languages.

## 11. Output Artifacts

Each processed document creates three primary files in `data/output/`:

- text output for direct reading,
- JSON output for downstream software or analysis,
- preprocessed image for debugging and inspection.

Evaluation also creates:

- overlay images in `data/output/boxes/` showing detected OCR regions.

These artifacts are valuable in a report because they show traceability from raw image to final answer.

## 12. What To Put In A PPT

If you are creating slides, use this structure:

1. Title slide: project name, your name, institution, date.
2. Problem statement: why document OCR is hard.
3. Objectives: accuracy, speed, readability, reproducibility.
4. Dataset: the three sample documents and ground truth labels.
5. System architecture: preprocessing, OCR, post-processing, evaluation.
6. Method details: grayscale, denoise, CLAHE, resize, deskew.
7. Recognition engine: EasyOCR on GPU.
8. Post-processing: confidence filtering and paragraph reconstruction.
9. Results: accuracy table and sample output screenshots.
10. Limitations and future work.
11. Conclusion.

Good figures for slides:

- original image vs preprocessed image,
- bounding box overlay image,
- OCR JSON excerpt,
- accuracy table for all three samples,
- architecture flow diagram.

## 13. What To Put In A Report

A strong report structure for this project is:

1. Abstract.
2. Introduction.
3. Problem definition.
4. Related background on OCR and document preprocessing.
5. Methodology.
6. Implementation details.
7. Experimental setup.
8. Results and discussion.
9. Limitations.
10. Conclusion and future work.

Important points to describe in the report:

- why preprocessing is needed before OCR,
- why GPU inference was chosen,
- how spatial ordering improves readability,
- how confidence filtering affects output quality,
- why evaluation uses word accuracy rather than raw character counts.

## 14. What To Put In A Book Chapter

If this project becomes a book chapter, the narrative should read like a case study:

### Suggested chapter flow

1. Introduce the practical OCR problem.
2. Explain document-image challenges such as skew, noise, and spacing.
3. Describe the preprocessing pipeline as a normalization stage.
4. Explain recognition with EasyOCR and the role of GPU acceleration.
5. Discuss post-processing as structure recovery.
6. Present the implementation and file layout.
7. Show experimental outputs and evaluation methodology.
8. Reflect on failure cases and future improvements.

### Themes worth emphasizing

- hybrid pipelines outperform single-step OCR on real documents,
- preprocessing can materially improve recognition quality,
- structured outputs are more useful than raw text alone,
- evaluation must include both quantitative and qualitative inspection.

## 15. Suggested Tables And Figures

For a polished report or chapter, include:

- a table of project configuration values,
- a table of sample images and file names,
- a results table with per-document accuracy,
- a before/after preprocessing figure,
- a sample JSON snippet,
- an architecture diagram,
- a limitations table.

## 16. Limitations

The current implementation is solid for printed English documents, but it is not a general-purpose OCR system.

Known limitations to mention:

- best tuned for printed documents rather than handwriting,
- English is the default OCR language,
- paragraph reconstruction is rule-based,
- evaluation uses a small sample set,
- performance depends on image quality and layout complexity.

## 17. Future Improvements

Natural next steps for the project are:

- support more languages,
- add handwriting support or a handwriting-specific model,
- improve paragraph segmentation with layout-aware heuristics,
- expose OCR results through a small UI or API,
- add more test documents and a larger evaluation set,
- compare EasyOCR against another OCR backend.

## 18. One-Paragraph Description For Reuse

This project implements an OCR pipeline for document images using OpenCV preprocessing, EasyOCR GPU inference, and custom post-processing to convert page images into structured text and JSON outputs. It also includes sample document generation and evaluation utilities that compare OCR output against ground truth, making it suitable as a reproducible case study for reports, presentations, and chapter-length technical documentation.

## 19. Final Verification Summary

The current repository state was verified by running the actual pipeline and evaluation on the bundled samples. The system processed all three images successfully and produced a mean word accuracy of 97.18%.

That makes the project ready for presentation and documentation work.
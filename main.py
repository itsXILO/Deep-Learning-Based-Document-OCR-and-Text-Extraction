import argparse

from config import DATA_INPUT_DIR, DATA_OUTPUT_DIR, OcrConfig, PipelineConfig, PreprocessingConfig
from src.pipeline import process_folder


def main():
    parser = argparse.ArgumentParser(description="OCR an image folder into per-image .txt + .json")
    parser.add_argument("input", nargs="?", default=str(DATA_INPUT_DIR), help="input folder with images")
    parser.add_argument("output", nargs="?", default=str(DATA_OUTPUT_DIR), help="output folder")
    parser.add_argument("--no-gpu", action="store_true", help="run on CPU")
    parser.add_argument("--min-confidence", type=float, default=None, help="min confidence to keep a line")
    parser.add_argument("--no-deskew", action="store_true", help="disable deskewing")
    parser.add_argument("--languages", type=str, default=None, help="comma-separated languages")
    args = parser.parse_args()

    pipeline_config = PipelineConfig(
        preprocessing=PreprocessingConfig(deskew=not args.no_deskew),
        ocr=OcrConfig(
            languages=(args.languages.split(",") if args.languages else ["en"]),
            use_gpu=not args.no_gpu,
            min_confidence=(args.min_confidence if args.min_confidence is not None else 0.4),
        ),
        input_dir=args.input,
        output_dir=args.output,
    )
    results = process_folder(args.input, args.output, pipeline_config)
    print(f"\nProcessed {len(results)} images -> {args.output}")


if __name__ == "__main__":
    main()
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_INPUT_DIR = PROJECT_ROOT / "data" / "input"
DATA_OUTPUT_DIR = PROJECT_ROOT / "data" / "output"


@dataclass
class PreprocessingConfig:
    target_width: int = 1600
    clahe_clip_limit: float = 2.0
    clahe_grid_size: tuple = (8, 8)
    denoise_h: float = 10.0
    deskew: bool = True


@dataclass
class OcrConfig:
    languages: list = field(default_factory=lambda: ["en"])
    use_gpu: bool = True
    min_confidence: float = 0.4
    paragraph: bool = False


@dataclass
class PipelineConfig:
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    ocr: OcrConfig = field(default_factory=OcrConfig)
    input_dir: Path = DATA_INPUT_DIR
    output_dir: Path = DATA_OUTPUT_DIR
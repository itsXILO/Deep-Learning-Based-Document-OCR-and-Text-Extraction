import cv2
import numpy as np
from config import PreprocessingConfig


def to_grayscale(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def denoise(image: np.ndarray, h: float = 10.0) -> np.ndarray:
    return cv2.fastNlMeansDenoising(image, None, h, 7, 21)


def adaptive_contrast(image: np.ndarray, clip_limit: float = 2.0, grid_size: tuple = (8, 8)) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
    return clahe.apply(image)


def resize_to_width(image: np.ndarray, target_width: int) -> np.ndarray:
    if target_width <= 0 or image.shape[1] == target_width:
        return image
    scale = target_width / image.shape[1]
    new_height = int(round(image.shape[0] * scale))
    return cv2.resize(image, (target_width, new_height), interpolation=cv2.INTER_AREA)


def deskew(image: np.ndarray) -> np.ndarray:
    gray = image if len(image.shape) == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    coords = cv2.findNonZero(thresh)
    if coords is None:
        return image
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    if -0.5 <= angle <= 0.5:
        return image
    height, width = gray.shape
    center = (width // 2, height // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, matrix, (width, height), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def preprocess(image: np.ndarray, config: PreprocessingConfig) -> np.ndarray:
    result = to_grayscale(image)
    if config.denoise_h > 0:
        result = denoise(result, config.denoise_h)
    result = adaptive_contrast(result, config.clahe_clip_limit, config.clahe_grid_size)
    result = resize_to_width(result, config.target_width)
    if config.deskew:
        result = deskew(result)
    return result


def preprocess_image(path, config: PreprocessingConfig) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {path}")
    return preprocess(image, config)
from __future__ import annotations

import cv2
import numpy as np
from PIL import Image
import imagehash


def try_read_image(path: str):
    """
    Reads an image using OpenCV.
    Returns:
        np.ndarray (BGR) if readable, otherwise None.
    """
    img = cv2.imread(path)
    return img  # None if unreadable/corrupted


def to_gray(bgr_img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)


def blur_score_laplacian(gray_img: np.ndarray) -> float:
    """
    Blur score using variance of Laplacian.
    Lower values usually mean blurrier images.
    """
    return float(cv2.Laplacian(gray_img, cv2.CV_64F).var())


def mean_brightness(gray_img: np.ndarray) -> float:
    """
    Average brightness (0-255) of grayscale image.
    """
    return float(np.mean(gray_img))


def perceptual_hash(path: str) -> str:
    """
    Perceptual hash for duplicate detection.
    """
    pil_img = Image.open(path).convert("RGB")
    return str(imagehash.phash(pil_img))

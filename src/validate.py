from __future__ import annotations

import os
import pandas as pd
from tqdm import tqdm

from .config import (
    ALLOWED_LABELS,
    MIN_WIDTH, MIN_HEIGHT,
    BLUR_LAPLACIAN_VAR_MIN,
    MEAN_BRIGHTNESS_MIN, MEAN_BRIGHTNESS_MAX,
)
from .utils_image import (
    try_read_image, to_gray,
    blur_score_laplacian, mean_brightness,
    perceptual_hash,
)


def _issue(code: str, image_id: str, message: str, severity: str):
    return {
        "issue_code": code,
        "image_id": image_id,
        "severity": severity,
        "message": message,
    }


def validate_dataset(images_dir: str = "data/raw", labels_csv: str = "data/raw/labels.csv"):
    """
    Returns:
      labels_df: DataFrame from labels_csv
      issues_df: DataFrame of detected issues with default status=open
    """
    if not os.path.exists(labels_csv):
        raise FileNotFoundError(f"Missing labels file: {labels_csv}")

    labels_df = pd.read_csv(labels_csv)
    issues = []

    required_cols = ["image_id", "label", "source", "collected_at", "consent", "notes"]
    for col in required_cols:
        if col not in labels_df.columns:
            issues.append(_issue("MISSING_COLUMN", "", f"labels.csv missing column '{col}'", "high"))

    if "image_id" not in labels_df.columns:
        return labels_df, pd.DataFrame(issues)

    # Row-wise checks: file exists, label allowed, consent
    for _, row in labels_df.iterrows():
        image_id = str(row.get("image_id", "")).strip()
        label = str(row.get("label", "")).strip()
        consent = str(row.get("consent", "")).strip().lower()

        if not image_id:
            issues.append(_issue("MISSING_IMAGE_ID", "", "Empty image_id in labels.csv", "high"))
            continue

        img_path = os.path.join(images_dir, image_id)
        if not os.path.exists(img_path):
            issues.append(_issue("FILE_MISSING", image_id, f"Image not found: {img_path}", "high"))

        if label not in ALLOWED_LABELS:
            issues.append(_issue("INVALID_LABEL", image_id, f"Label '{label}' not in allowed list", "high"))

        if consent != "yes":
            issues.append(_issue("CONSENT_NOT_YES", image_id, f"Consent is '{consent}' (expected 'yes')", "high"))

    # Image-based checks: corrupt, resolution, blur, brightness, duplicates
    hash_map = {}  # phash -> first_image_id

    image_ids = labels_df["image_id"].astype(str).tolist()
    for image_id in tqdm(image_ids, desc="Validating images"):
        img_path = os.path.join(images_dir, image_id)
        if not os.path.exists(img_path):
            continue

        img = try_read_image(img_path)
        if img is None:
            issues.append(_issue("CORRUPT_IMAGE", image_id, "OpenCV cannot read this file", "high"))
            continue

        h, w = img.shape[:2]
        if w < MIN_WIDTH or h < MIN_HEIGHT:
            issues.append(_issue("LOW_RESOLUTION", image_id, f"{w}x{h} below {MIN_WIDTH}x{MIN_HEIGHT}", "medium"))

        gray = to_gray(img)

        bscore = blur_score_laplacian(gray)
        if bscore < BLUR_LAPLACIAN_VAR_MIN:
            issues.append(_issue("BLURRY", image_id, f"LaplacianVar={bscore:.1f} < {BLUR_LAPLACIAN_VAR_MIN}", "medium"))

        mb = mean_brightness(gray)
        if mb < MEAN_BRIGHTNESS_MIN:
            issues.append(_issue("TOO_DARK", image_id, f"MeanBrightness={mb:.1f} < {MEAN_BRIGHTNESS_MIN}", "low"))
        elif mb > MEAN_BRIGHTNESS_MAX:
            issues.append(_issue("TOO_BRIGHT", image_id, f"MeanBrightness={mb:.1f} > {MEAN_BRIGHTNESS_MAX}", "low"))

        # duplicates via perceptual hash
        try:
            ph = perceptual_hash(img_path)
            if ph in hash_map:
                issues.append(_issue("DUPLICATE", image_id, f"Duplicate of {hash_map[ph]} (pHash={ph})", "medium"))
            else:
                hash_map[ph] = image_id
        except Exception as e:
            issues.append(_issue("HASH_FAILED", image_id, f"pHash failed: {e}", "low"))

    issues_df = pd.DataFrame(issues)
    if not issues_df.empty:
        issues_df["status"] = "open"

    return labels_df, issues_df

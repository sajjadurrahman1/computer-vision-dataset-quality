# CV Dataset Governance & Quality Pipeline

This project validates a small computer vision dataset (hand gestures) with a focus on:
- data completeness
- label correctness
- image quality
- traceability (audit log + versioned releases)

## Dataset structure
- `data/raw/` -> images + `labels.csv`
- `data/releases/` -> timestamped dataset snapshots

`labels.csv` columns:
- image_id, label, source, collected_at, consent, notes

## What it checks
- missing files
- corrupted images
- invalid labels
- consent != yes
- low resolution
- blur (Laplacian variance)
- too dark / too bright
- duplicates (perceptual hash)

## Outputs
- `reports/issues.csv` (issue tracker)
- `reports/quality_report.xlsx` (KPIs + distributions)
- `logs/audit_log.csv` (run history)
- `data/releases/release_<timestamp>/` (snapshots)

## Run
1) Install:
   `pip install -r requirements.txt`

2) (Optional) collect data:
   `python -m src.collect_webcam`

3) Run pipeline:
   `python run_pipeline.py`

from __future__ import annotations

import os
import pandas as pd
from datetime import datetime

from src.validate import validate_dataset
from src.report_excel import write_excel_report
from src.versioning import create_release_copy


def _append_audit_log(row: dict, path: str = "logs/audit_log.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        df = pd.read_csv(path)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])

    df.to_csv(path, index=False)


def _preserve_issue_status(new_issues_df: pd.DataFrame, issues_csv_path: str) -> pd.DataFrame:
    """
    Preserve 'status' from previous runs, matching by (issue_code, image_id).
    """
    if new_issues_df.empty:
        return new_issues_df

    if not os.path.exists(issues_csv_path):
        return new_issues_df

    old_df = pd.read_csv(issues_csv_path)
    if old_df.empty or "status" not in old_df.columns:
        return new_issues_df

    # Build lookup
    old_map = {}
    for _, r in old_df.iterrows():
        key = (str(r.get("issue_code", "")), str(r.get("image_id", "")))
        old_map[key] = str(r.get("status", "open"))

    statuses = []
    for _, r in new_issues_df.iterrows():
        key = (str(r.get("issue_code", "")), str(r.get("image_id", "")))
        statuses.append(old_map.get(key, "open"))

    new_issues_df["status"] = statuses
    return new_issues_df


def main():
    labels_df, issues_df = validate_dataset()

    os.makedirs("reports", exist_ok=True)
    issues_csv = "reports/issues.csv"

    # preserve issue status across runs
    issues_df = _preserve_issue_status(issues_df, issues_csv)

    issues_df.to_csv(issues_csv, index=False)

    excel_out = write_excel_report(labels_df, issues_df, out_path="reports/quality_report.xlsx")
    release_path = create_release_copy()

    audit_row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "release_path": release_path,
        "label_rows": len(labels_df),
        "issues_total": len(issues_df),
        "issues_open": int((issues_df["status"] == "open").sum()) if not issues_df.empty else 0,
        "issues_resolved": int((issues_df["status"] == "resolved").sum()) if not issues_df.empty else 0,
    }
    _append_audit_log(audit_row)

    print("✅ Pipeline complete")
    print(f"- Issues CSV: {issues_csv}")
    print(f"- Excel report: {excel_out}")
    print(f"- Release snapshot: {release_path}")
    print(f"- Audit log: logs/audit_log.csv")


if __name__ == "__main__":
    main()

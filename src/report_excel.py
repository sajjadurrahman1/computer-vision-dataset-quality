from __future__ import annotations

import os
import pandas as pd


def write_excel_report(labels_df: pd.DataFrame, issues_df: pd.DataFrame, out_path: str = "reports/quality_report.xlsx") -> str:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    total_rows = len(labels_df)
    total_issues = len(issues_df)

    open_issues = 0
    resolved_issues = 0
    if not issues_df.empty and "status" in issues_df.columns:
        open_issues = int((issues_df["status"] == "open").sum())
        resolved_issues = int((issues_df["status"] == "resolved").sum())

    kpis = pd.DataFrame([{
        "total_label_rows": total_rows,
        "issues_total": total_issues,
        "issues_open": open_issues,
        "issues_resolved": resolved_issues,
    }])

    label_dist = pd.DataFrame()
    if "label" in labels_df.columns:
        label_dist = labels_df["label"].value_counts(dropna=False).reset_index()
        label_dist.columns = ["label", "count"]

    severity_dist = pd.DataFrame()
    if not issues_df.empty and "severity" in issues_df.columns:
        severity_dist = issues_df["severity"].value_counts(dropna=False).reset_index()
        severity_dist.columns = ["severity", "count"]

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        kpis.to_excel(writer, sheet_name="KPIs", index=False)
        if not label_dist.empty:
            label_dist.to_excel(writer, sheet_name="LabelDistribution", index=False)
        if not severity_dist.empty:
            severity_dist.to_excel(writer, sheet_name="IssueSeverity", index=False)

        labels_df.to_excel(writer, sheet_name="Labels", index=False)
        issues_df.to_excel(writer, sheet_name="Issues", index=False)

    return out_path

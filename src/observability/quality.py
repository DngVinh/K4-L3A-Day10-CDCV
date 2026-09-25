from __future__ import annotations

from pathlib import Path
from typing import Any

import great_expectations as gx
from great_expectations import expectations as gxe

import pandas as pd

from core.config import Settings
from core.utils import safe_slug, write_json


REQUIRED_COLUMNS = ("paper_id", "title", "text_for_embedding", "summary")
MAX_STALE_RATIO = 0.25


def _quality_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare text for validation without changing the caller's dataframe."""
    checked = df.copy()
    for column in REQUIRED_COLUMNS:
        if column not in checked:
            checked[column] = None
        checked[column] = checked[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
    for column in ("paper_id", "title", "text_for_embedding"):
        checked[column] = checked[column].replace("", None)
    checked["summary"] = checked["summary"].fillna("").astype(str)
    return checked


def _freshness_payload(df: pd.DataFrame, settings: Settings) -> dict[str, Any]:
    total_rows = len(df)
    published = (
        pd.to_datetime(df["published"], errors="coerce", utc=True)
        if "published" in df
        else pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns, UTC]")
    )
    if "age_days" in df:
        ages = pd.to_numeric(df["age_days"], errors="coerce")
    else:
        ages = (pd.Timestamp.now(tz="UTC") - published).dt.days

    unknown_rows = int(ages.isna().sum())
    stale_rows = int(ages.gt(settings.freshness_threshold_days).sum())
    stale_ratio = stale_rows / total_rows if total_rows else 0.0
    valid_dates = published.dropna()
    return {
        "latest_published": valid_dates.max().date().isoformat() if not valid_dates.empty else None,
        "oldest_published": valid_dates.min().date().isoformat() if not valid_dates.empty else None,
        "stale_rows": stale_rows,
        "unknown_age_rows": unknown_rows,
        "total_rows": total_rows,
        "stale_ratio": stale_ratio,
        "freshness_threshold_days": settings.freshness_threshold_days,
        "max_stale_ratio": MAX_STALE_RATIO,
        "is_fresh": total_rows > 0 and unknown_rows == 0 and stale_ratio <= MAX_STALE_RATIO,
    }


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """Validate a dataset using GX 1.x and persist a compact quality report."""
    checked = _quality_frame(df)
    context = gx.get_context(mode="ephemeral")
    source = context.data_sources.add_pandas(name="papers_source")
    asset = source.add_dataframe_asset(name="papers_asset")
    batch_definition = asset.add_batch_definition_whole_dataframe("papers_batch")
    batch = batch_definition.get_batch(batch_parameters={"dataframe": checked})

    expectations = [
        gxe.ExpectTableRowCountToBeBetween(min_value=5, max_value=5000),
        *(gxe.ExpectColumnValuesToNotBeNull(column=column) for column in REQUIRED_COLUMNS[:3]),
        gxe.ExpectColumnValuesToBeUnique(column="paper_id"),
        gxe.ExpectColumnValueLengthsToBeBetween(column="summary", min_value=30),
    ]
    checks = []
    for expectation in expectations:
        result = batch.validate(expectation)
        checks.append(
            {
                "expectation": type(expectation).__name__,
                "column": getattr(expectation, "column", None),
                "success": bool(result.success),
            }
        )

    payload = {
        "report_name": report_name,
        "success": all(check["success"] for check in checks),
        "checks": checks,
        "freshness": _freshness_payload(df, settings),
    }
    report_path = settings.paths.quality_dir / f"{safe_slug(report_name)}_quality_report.json"
    write_json(report_path, payload)
    return payload


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path: Path) -> dict[str, Any]:
    """Record the publication date range and the freshness SLA status."""
    payload = _freshness_payload(df, settings)
    write_json(Path(report_path), payload)
    return payload

from __future__ import annotations

from math import ceil

import pandas as pd

from core.utils import write_json


_REQUIRED_COLUMNS = {
    "paper_id",
    "title",
    "summary",
    "published",
    "authors_joined",
    "categories_joined",
}
_SCENARIO_FRACTION = 0.20
_NOISE = " ###CORRUPTED_TEXT_9x!@# ### "


def _affected_count(row_count: int) -> int:
    return max(1, ceil(row_count * _SCENARIO_FRACTION))


def _sample_indices(df: pd.DataFrame, count: int, seed: int) -> list[int]:
    return df.sample(n=min(count, len(df)), random_state=seed).index.tolist()


def _rebuild_embedding_text(df: pd.DataFrame) -> None:
    df["text_for_embedding"] = (
        "Title: "
        + df["title"].fillna("").astype(str)
        + "\nAuthors: "
        + df["authors_joined"].fillna("").astype(str)
        + "\nPublished: "
        + df["published"].fillna("").astype(str)
        + "\nCategories: "
        + df["categories_joined"].fillna("").astype(str)
        + "\nSummary: "
        + df["summary"].fillna("").astype(str)
    )


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path) -> pd.DataFrame:
    """Apply six deterministic corruption scenarios and write an audit log.

    The input dataframe is never mutated.  A fixed seed makes the same source
    dataset produce the same corrupted dataset and log, which keeps the
    baseline/corrupted/repaired comparison reproducible.
    """
    missing_columns = _REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Cleaned dataset is missing required columns: {missing}.")
    if df.empty:
        raise ValueError("Cannot corrupt an empty cleaned dataset.")

    corrupted = df.copy(deep=True).reset_index(drop=True)
    source_rows = len(corrupted)
    log: list[dict[str, object]] = []

    # 1. Simulate lost recent data before applying row-level corruptions.
    latest_count = _affected_count(source_rows)
    published_dates = pd.to_datetime(corrupted["published"], errors="coerce", utc=True)
    latest_indices = published_dates.sort_values(ascending=False, na_position="last").head(latest_count).index
    dropped_paper_ids = corrupted.loc[latest_indices, "paper_id"].astype(str).tolist()
    corrupted = corrupted.drop(index=latest_indices).reset_index(drop=True)
    log.append(
        {
            "scenario": "drop_latest_records",
            "description": "Removed the newest 20% of records.",
            "affected_paper_ids": dropped_paper_ids,
            "count": len(dropped_paper_ids),
        }
    )

    affected_count = _affected_count(len(corrupted))

    # 2. Blank summaries.
    blank_indices = _sample_indices(corrupted, affected_count, seed=11)
    blank_paper_ids = corrupted.loc[blank_indices, "paper_id"].astype(str).tolist()
    corrupted.loc[blank_indices, "summary"] = ""
    log.append(
        {
            "scenario": "blank_summary",
            "description": "Cleared summaries for selected records.",
            "affected_paper_ids": blank_paper_ids,
            "count": len(blank_paper_ids),
        }
    )

    # 3. Add text noise to summaries.
    noise_indices = _sample_indices(corrupted, affected_count, seed=23)
    noise_paper_ids = corrupted.loc[noise_indices, "paper_id"].astype(str).tolist()
    corrupted.loc[noise_indices, "summary"] = (
        corrupted.loc[noise_indices, "summary"].fillna("").astype(str) + _NOISE
    )
    log.append(
        {
            "scenario": "inject_noise",
            "description": "Appended a synthetic noise marker to summaries.",
            "affected_paper_ids": noise_paper_ids,
            "count": len(noise_paper_ids),
            "noise_marker": _NOISE.strip(),
        }
    )

    # 4. Truncate titles below the quality threshold of eight characters.
    title_indices = _sample_indices(corrupted, affected_count, seed=37)
    title_paper_ids = corrupted.loc[title_indices, "paper_id"].astype(str).tolist()
    corrupted.loc[title_indices, "title"] = corrupted.loc[title_indices, "title"].fillna("").astype(str).str.slice(0, 7)
    log.append(
        {
            "scenario": "truncate_title",
            "description": "Shortened titles to at most seven characters.",
            "affected_paper_ids": title_paper_ids,
            "count": len(title_paper_ids),
        }
    )

    # 5. Make selected records stale by moving their publication date back one year.
    stale_indices = _sample_indices(corrupted, affected_count, seed=53)
    stale_paper_ids = corrupted.loc[stale_indices, "paper_id"].astype(str).tolist()
    stale_dates = pd.to_datetime(corrupted.loc[stale_indices, "published"], errors="coerce", utc=True)
    corrupted.loc[stale_indices, "published"] = (stale_dates - pd.Timedelta(days=365)).dt.date.astype(str)
    log.append(
        {
            "scenario": "stale_date",
            "description": "Moved publication dates back by 365 days.",
            "affected_paper_ids": stale_paper_ids,
            "count": len(stale_paper_ids),
            "days_shifted": 365,
        }
    )

    # 6. Duplicate rows last, so duplicate identifiers remain visible to quality checks.
    duplicate_indices = _sample_indices(corrupted, affected_count, seed=71)
    duplicates = corrupted.loc[duplicate_indices].copy()
    duplicate_paper_ids = duplicates["paper_id"].astype(str).tolist()
    corrupted = pd.concat([corrupted, duplicates], ignore_index=True)
    _rebuild_embedding_text(corrupted)
    log.append(
        {
            "scenario": "duplicate_rows",
            "description": "Duplicated complete records without changing paper_id.",
            "affected_paper_ids": duplicate_paper_ids,
            "count": len(duplicate_paper_ids),
        }
    )

    write_json(
        output_log_path,
        {
            "source_rows": source_rows,
            "corrupted_rows": len(corrupted),
            "scenarios": log,
        },
    )
    return corrupted

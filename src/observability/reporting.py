from __future__ import annotations

from pathlib import Path
from typing import Any

from core.utils import write_text


METRICS = ("samples", "retrieval_hit_rate", "mean_token_f1", "judge_accuracy", "mean_judge_score")


def _display(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, bool):
        return "PASS" if value else "FAIL"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value).replace("|", "\\|").replace("\n", " ")


def _metric_rows(*states: dict[str, Any]) -> list[str]:
    return [
        "| `" + metric + "` | " + " | ".join(_display(state.get(metric)) for state in states) + " |"
        for metric in METRICS
    ]


def _quality_rows(quality: dict[str, Any]) -> list[str]:
    return [
        f"| {item.get('expectation', 'N/A')} | {_display(item.get('column'))} | {_display(item.get('success'))} |"
        for item in quality.get("checks", [])
    ]


def _failed_checks(quality: dict[str, Any]) -> str:
    failures = [
        f"{item.get('expectation', 'unknown')}({item.get('column') or 'table'})"
        for item in quality.get("checks", [])
        if item.get("success") is False
    ]
    return ", ".join(failures) if failures else "Không có"


def _difference(left: dict[str, Any], right: dict[str, Any], key: str) -> str:
    first, second = left.get(key), right.get(key)
    if not isinstance(first, (int, float)) or not isinstance(second, (int, float)):
        return "N/A"
    return f"{second - first:+.3f}"


def generate_phase1_report(
    report_path,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    """Write a baseline report from the actual pipeline outputs."""
    lines = [
        "# Báo cáo Baseline",
        "",
        "## Nguồn dữ liệu",
        "",
        "| Trường | Giá trị |",
        "| --- | --- |",
        *(f"| {_display(key)} | {_display(value)} |" for key, value in source_summary.items()),
        "",
        "## Chỉ số đánh giá",
        "",
        "| Metric | Baseline |",
        "| --- | ---: |",
        *_metric_rows(metrics),
        "",
        "## Kiểm định dữ liệu",
        "",
        f"**Quality Gate:** {_display(quality.get('success'))}",
        "",
        "| Expectation | Cột | Kết quả |",
        "| --- | --- | --- |",
        *_quality_rows(quality),
        "",
        "## Freshness SLA",
        "",
        "| Thuộc tính | Giá trị |",
        "| --- | --- |",
        *(f"| `{key}` | {_display(value)} |" for key, value in freshness.items()),
        "",
    ]
    write_text(Path(report_path), "\n".join(lines))


def generate_corruption_report(
    report_path,
    baseline_metrics: dict[str, Any],
    corrupted_metrics: dict[str, Any],
    repaired_metrics: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    corrupted_freshness: dict[str, Any],
    repaired_freshness: dict[str, Any],
) -> None:
    """Compare all three runs without assuming that corruption or repair succeeded."""
    lines = [
        "# Báo cáo đối chiếu dữ liệu",
        "",
        "## Baseline vs Corrupted vs Repaired",
        "",
        "| Metric | Baseline | Corrupted | Repaired |",
        "| --- | ---: | ---: | ---: |",
        *_metric_rows(baseline_metrics, corrupted_metrics, repaired_metrics),
        "",
        "## Quality Gate và Freshness SLA",
        "",
        "| Signal | Corrupted | Repaired |",
        "| --- | ---: | ---: |",
        f"| Quality Gate | {_display(corrupted_quality.get('success'))} | {_display(repaired_quality.get('success'))} |",
        f"| Failed checks | {_display(_failed_checks(corrupted_quality))} | {_display(_failed_checks(repaired_quality))} |",
        f"| Freshness | {_display(corrupted_freshness.get('is_fresh'))} | {_display(repaired_freshness.get('is_fresh'))} |",
        f"| Stale rows | {_display(corrupted_freshness.get('stale_rows'))} | {_display(repaired_freshness.get('stale_rows'))} |",
        f"| Stale ratio | {_display(corrupted_freshness.get('stale_ratio'))} | {_display(repaired_freshness.get('stale_ratio'))} |",
        "",
        "## Chênh lệch so với baseline",
        "",
        "| Metric | Corrupted - Baseline | Repaired - Baseline |",
        "| --- | ---: | ---: |",
        *(
            f"| `{metric}` | {_difference(baseline_metrics, corrupted_metrics, metric)} | "
            f"{_difference(baseline_metrics, repaired_metrics, metric)} |"
            for metric in METRICS[1:]
        ),
        "",
        "Đối chiếu các chênh lệch trên với corruption log trước khi kết luận tác động và phục hồi.",
        "",
    ]
    write_text(Path(report_path), "\n".join(lines))

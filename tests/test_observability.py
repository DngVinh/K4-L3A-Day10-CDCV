from dataclasses import replace

import pandas as pd

from core.config import load_settings
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_corruption_report, generate_phase1_report


def _sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "paper_id": [f"10.1/{i}" for i in range(5)],
            "title": [f"Research paper {i}" for i in range(5)],
            "summary": ["A sufficiently detailed abstract about retrieval and evaluation."] * 5,
            "text_for_embedding": [f"Paper {i} context" for i in range(5)],
            "published": ["2026-09-01"] * 5,
            "age_days": [24] * 5,
        }
    )


def test_quality_gate_detects_corruption_and_freshness(tmp_path):
    base = load_settings()
    settings = replace(
        base,
        google_api_key=None,
        openai_api_key=None,
        anthropic_api_key=None,
        openrouter_api_key=None,
        custom_llm_api_key=None,
        paths=replace(base.paths, quality_dir=tmp_path),
    )
    clean = _sample_frame()
    clean_result = run_data_quality_checks(clean, settings, "baseline")
    assert clean_result["success"] is True
    assert clean_result["freshness"]["is_fresh"] is True
    assert (tmp_path / "baseline_quality_report.json").exists()

    corrupted = clean.copy()
    corrupted.loc[1, "paper_id"] = corrupted.loc[0, "paper_id"]
    corrupted.loc[2, "summary"] = ""
    corrupted.loc[3, "title"] = "  "
    corrupted.loc[1:3, "age_days"] = 365
    bad_result = run_data_quality_checks(corrupted, settings, "corrupted")
    assert bad_result["success"] is False
    failed = {(check["expectation"], check["column"]) for check in bad_result["checks"] if not check["success"]}
    assert ("ExpectColumnValuesToBeUnique", "paper_id") in failed
    assert ("ExpectColumnValuesToNotBeNull", "title") in failed
    assert ("ExpectColumnValueLengthsToBeBetween", "summary") in failed
    assert bad_result["freshness"]["is_fresh"] is False
    assert bad_result["freshness"]["stale_rows"] == 3
    freshness = build_freshness_report(corrupted, settings, tmp_path / "freshness.json")
    assert freshness["stale_ratio"] == 0.6
    assert (tmp_path / "corrupted_quality_report.json").exists()


def test_reports_render_supplied_values(tmp_path):
    metrics = {"samples": 10, "retrieval_hit_rate": 0.8, "mean_token_f1": 0.5}
    quality = {"success": True, "checks": [{"expectation": "unique", "column": "paper_id", "success": True}]}
    freshness = {"is_fresh": True, "stale_rows": 1, "stale_ratio": 0.1}
    baseline = tmp_path / "phase1.md"
    comparison = tmp_path / "corruption.md"
    generate_phase1_report(baseline, {"source": "snapshot"}, metrics, quality, freshness)
    generate_corruption_report(
        comparison, metrics, {**metrics, "retrieval_hit_rate": 0.3}, metrics,
        {"success": False}, quality, {"is_fresh": False, "stale_rows": 4, "stale_ratio": 0.4}, freshness,
    )
    assert "snapshot" in baseline.read_text(encoding="utf-8")
    assert "0.800" in baseline.read_text(encoding="utf-8")
    assert "| `retrieval_hit_rate` | 0.800 | 0.300 | 0.800 |" in comparison.read_text(encoding="utf-8")
    assert "| Quality Gate | FAIL | PASS |" in comparison.read_text(encoding="utf-8")
    assert "| `retrieval_hit_rate` | -0.500 | +0.000 |" in comparison.read_text(encoding="utf-8")

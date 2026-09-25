from __future__ import annotations

from datetime import UTC, datetime

from core.config import load_settings
from core.utils import write_csv, write_json
from evaluation.metrics import evaluate_pipeline
from evaluation.testset import build_test_set
from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import fetch_source_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_phase1_report
from retrieval.index import LocalEmbeddingIndex

def main() -> None:
    """Run the clean-data baseline pipeline from raw source to report."""
    settings = load_settings()
    records = fetch_source_records(settings)
    run_date = datetime.now(UTC)
    clean_df = build_clean_dataframe(records, run_date)
    if clean_df.empty:
        raise RuntimeError("Cleaning produced no valid records; baseline cannot continue.")

    write_csv(clean_df, settings.paths.clean_csv)
    write_json(settings.paths.clean_json, clean_df.to_dict(orient="records"))

    quality = run_data_quality_checks(clean_df, settings, "baseline")
    freshness = build_freshness_report(clean_df, settings, settings.paths.freshness_report)
    if not quality["success"]:
        raise RuntimeError("Baseline quality gate failed; refusing to build the serving index.")

    index = LocalEmbeddingIndex.build(clean_df, settings, settings.paths.embeddings_json)
    if settings.refresh_test_set or not settings.paths.eval_testset.exists():
        build_test_set(clean_df, settings.paths.eval_testset)
    metrics = evaluate_pipeline(
        settings,
        index,
        settings.paths.eval_testset,
        settings.paths.baseline_metrics,
        settings.paths.baseline_answers,
    )
    source_summary = {
        "source_api": settings.source_api,
        "query": settings.source_query,
        "records": len(records),
        "raw_records_path": str(settings.paths.raw_records_json),
        "run_at": run_date.isoformat(),
    }
    generate_phase1_report(
        settings.paths.baseline_report,
        source_summary,
        metrics.summary,
        quality,
        freshness,
    )
    print("Baseline pipeline completed.")
    print(
        f"Records: {len(clean_df)} | Hit rate: {metrics.summary['retrieval_hit_rate']:.4f} | "
        f"Token F1: {metrics.summary['mean_token_f1']:.4f}"
    )
    print(f"Report: {settings.paths.baseline_report}")

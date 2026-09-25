from datetime import UTC, datetime, timedelta

import pandas as pd

from core.config import load_settings
from ingestion.corruption import corrupt_clean_dataframe
from observability.quality import MAX_STALE_RATIO, build_freshness_report
from retrieval.index import SearchResult
from retrieval.qa import _extract_answer


def test_corruption_triggers_freshness_sla_without_mutating_baseline(tmp_path):
    today = datetime.now(UTC).date()
    recent = (today - timedelta(days=20)).isoformat()
    clean = pd.DataFrame(
        {
            "paper_id": [f"10.1/{i}" for i in range(24)],
            "title": [f"Research paper {i}" for i in range(24)],
            "summary": ["A sufficiently detailed abstract about retrieval and evaluation."] * 24,
            "published": [recent] * 24,
            "age_days": [20] * 24,
            "authors_joined": ["Example Author"] * 24,
            "categories_joined": ["Research"] * 24,
            "text_for_embedding": ["Title and summary"] * 24,
        }
    )
    original = clean.copy(deep=True)
    corrupted = corrupt_clean_dataframe(clean, tmp_path / "corruption_log.json")
    freshness = build_freshness_report(
        corrupted, load_settings(), tmp_path / "freshness.json"
    )

    pd.testing.assert_frame_equal(clean, original)
    assert len(corrupted) == 23
    assert freshness["stale_ratio"] > MAX_STALE_RATIO
    assert freshness["is_fresh"] is False
    shifted = corrupted["published"].eq((today - timedelta(days=385)).isoformat())
    assert shifted.sum() >= 6
    assert corrupted.loc[shifted, "age_days"].eq(385).all()


def test_author_question_uses_author_metadata():
    result = SearchResult(
        paper_id="10.1/1",
        title="Research paper",
        score=1.0,
        content="Paper context",
        metadata={
            "authors_joined": "Ada Lovelace, Grace Hopper",
            "published": "2026-09-01",
            "categories_joined": "Computer Science",
            "summary": "A paper about computing history.",
        },
    )
    question = "Who are the authors of the paper 'Research paper'?"
    assert _extract_answer(question, result) == "Ada Lovelace, Grace Hopper"

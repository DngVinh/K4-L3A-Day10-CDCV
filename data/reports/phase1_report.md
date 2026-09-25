# Báo cáo Baseline

## Nguồn dữ liệu

| Trường | Giá trị |
| --- | --- |
| source_api | Crossref REST API |
| source_mode | offline snapshot |
| query | agentic retrieval augmented generation large language model |
| records | 24 |
| raw_records_path | data/raw/crossref_records.json |
| run_at | 2026-09-25T09:37:19.041846+00:00 |

## Chỉ số đánh giá

| Metric | Baseline |
| --- | ---: |
| `samples` | 10 |
| `retrieval_hit_rate` | 1.000 |
| `mean_token_f1` | 1.000 |
| `judge_accuracy` | 1.000 |
| `mean_judge_score` | 5 |

## Kiểm định dữ liệu

**Quality Gate:** PASS

| Expectation | Cột | Kết quả |
| --- | --- | --- |
| ExpectTableRowCountToBeBetween | N/A | PASS |
| ExpectColumnValuesToNotBeNull | paper_id | PASS |
| ExpectColumnValuesToNotBeNull | title | PASS |
| ExpectColumnValuesToNotBeNull | text_for_embedding | PASS |
| ExpectColumnValuesToBeUnique | paper_id | PASS |
| ExpectColumnValueLengthsToBeBetween | summary | PASS |

## Freshness SLA

| Thuộc tính | Giá trị |
| --- | --- |
| `latest_published` | 2026-07-22 |
| `oldest_published` | 2026-03-28 |
| `stale_rows` | 1 |
| `unknown_age_rows` | 0 |
| `total_rows` | 24 |
| `stale_ratio` | 0.042 |
| `freshness_threshold_days` | 180 |
| `max_stale_ratio` | 0.250 |
| `is_fresh` | PASS |

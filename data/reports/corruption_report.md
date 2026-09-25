# Báo cáo đối chiếu dữ liệu

## Baseline vs Corrupted vs Repaired

| Metric | Baseline | Corrupted | Repaired |
| --- | ---: | ---: | ---: |
| `samples` | 10 | 10 | 10 |
| `retrieval_hit_rate` | 1.000 | 0.400 | 1.000 |
| `mean_token_f1` | 1.000 | 0.653 | 1.000 |
| `judge_accuracy` | 1.000 | 0.700 | 1.000 |
| `mean_judge_score` | 5 | 3.400 | 5 |

## Quality Gate và Freshness SLA

| Signal | Corrupted | Repaired |
| --- | ---: | ---: |
| Quality Gate | FAIL | PASS |
| Failed checks | ExpectColumnValuesToBeUnique(paper_id), ExpectColumnValueLengthsToBeBetween(summary) | Không có |
| Freshness | FAIL | PASS |
| Stale rows | 7 | 1 |
| Stale ratio | 0.304 | 0.042 |

## Chênh lệch so với baseline

| Metric | Corrupted - Baseline | Repaired - Baseline |
| --- | ---: | ---: |
| `retrieval_hit_rate` | -0.600 | +0.000 |
| `mean_token_f1` | -0.347 | +0.000 |
| `judge_accuracy` | -0.300 | +0.000 |
| `mean_judge_score` | -1.600 | +0.000 |

Đối chiếu các chênh lệch trên với corruption log trước khi kết luận tác động và phục hồi.

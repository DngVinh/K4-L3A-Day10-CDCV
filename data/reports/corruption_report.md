# Corruption and Repair Report

The same evaluation set is used for all three states.

## Metrics comparison

| Metric | Baseline | Corrupted | Repaired | Corruption delta | Repair delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| `retrieval_hit_rate` | 1.0000 | 0.4000 | 1.0000 | -0.6000 | +0.6000 |
| `mean_token_f1` | 1.0000 | 0.6788 | 1.0000 | -0.3212 | +0.3212 |
| `judge_accuracy` | 1.0000 | 0.7000 | 1.0000 | -0.3000 | +0.3000 |
| `mean_judge_score` | 5.0000 | 3.6000 | 5.0000 | -1.4000 | +1.4000 |

## Quality and freshness signals

| Signal | Baseline | Corrupted | Repaired |
| --- | --- | --- | --- |
| Quality checks pass | — | FAIL | PASS |
| Freshness status | — | STALE | FRESH |

## Interpretation

- Corruption is observable when quality or freshness changes and the RAG metrics degrade.
- Repair rebuilds the clean dataframe from the trusted raw snapshot, then recreates the vector index.
- A successful repair is indicated by restored quality/freshness and recovered evaluation metrics.

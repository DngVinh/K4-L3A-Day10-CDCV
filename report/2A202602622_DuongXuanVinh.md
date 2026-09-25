# Báo cáo cá nhân — Dương Xuân Vinh

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Dương Xuân Vinh |
| MSSV | 2A202602622 |
| Khóa/Lớp | K4-L3-DAY10 |
| Tên nhóm | CDCV |
| Vai trò chính | Trưởng nhóm / TV5 — Pipeline integration & evidence owner |
| Repository | <https://github.com/DngVinh/K4-L3A-Day10-CDCV> |
| Ngày hoàn thành | 2026-09-25 |

## 2. Vai trò và phạm vi công việc

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Baseline orchestration | `src/pipelines/phase1.py` | Raw records, clean schema, evaluation set | Baseline answers, metrics, quality/freshness reports | Hoàn thành |
| Corruption–repair integration | `src/pipelines/corruption_flow.py` | Baseline artifacts và corruption scenarios | Corrupted/repaired answers, metrics và comparison report | Hoàn thành |
| Reproducibility/evidence | `script/run_phase1.py`, `script/run_corruption_flow.py` | Python 3.13 environment | Lệnh chạy và artifacts xác minh | Hoàn thành |

## 3. Kết quả theo vai trò

Đã tái hiện toàn bộ flow:

```text
Crossref/raw snapshot
    -> cleaning
    -> embedding/index
    -> baseline evaluation
    -> quality/freshness checks
    -> corruption
    -> re-index/re-evaluate
    -> repair từ raw snapshot
    -> comparison report
```

Các bằng chứng chính:

- `data/reports/phase1_report.md`
- `data/reports/corruption_report.md`
- `data/results/baseline_metrics.json`
- `data/results/corrupted_metrics.json`
- `data/results/repaired_metrics.json`
- `data/quality/baseline_quality_report.json`
- `data/quality/corrupted_quality_report.json`
- `data/quality/repaired_quality_report.json`

## 4. Giải thích phần kỹ thuật

`phase1.py` điều phối pipeline baseline từ raw snapshot đến cleaning, embedding/index, evaluation và quality/freshness reports. `corruption_flow.py` chạy cùng evaluation set qua ba trạng thái baseline, corrupted và repaired để so sánh công bằng. Repair được thực hiện bằng cách dựng lại dữ liệu sạch từ nguồn raw tin cậy rồi tạo lại index.

Contract tích hợp chính:

| Thành phần | Mô tả |
| --- | --- |
| Input | Raw Crossref snapshot và `data/eval/test_set.json` |
| Output | Cleaned data, embeddings, answers, metrics, quality/freshness và reports |
| Module phụ thuộc | Ingestion, cleaning, retrieval, evaluation, observability |
| Module sử dụng output | Reports và bước tổng hợp kết quả |
| Điều kiện lỗi | Dữ liệu corrupted làm quality gate hoặc freshness fail; repair phải khôi phục artifact và metrics |

## 5. Cách xác minh

Môi trường xác minh: Python 3.13.15, Great Expectations 1.23.1.

```powershell
$env:PYTHONPATH = 'src'
& '.\.venv-py313\Scripts\python.exe' script/run_phase1.py
& '.\.venv-py313\Scripts\python.exe' script/run_corruption_flow.py
```

Kết quả thực tế:

- Baseline: 24 records, quality PASS, retrieval hit rate `1.0000`.
- Corrupted: quality FAIL, freshness STALE, retrieval hit rate `0.4000`.
- Repaired: 24 records, quality PASS, freshness FRESH, retrieval hit rate `1.0000`.

## 6. Metrics và phân tích

| Metric/signal | Baseline | Corrupted | Repaired |
| --- | ---: | ---: | ---: |
| `retrieval_hit_rate` | 1.0000 | 0.4000 | 1.0000 |
| `mean_token_f1` | 1.0000 | 0.6788 | 1.0000 |
| `judge_accuracy` | 1.0000 | 0.7000 | 1.0000 |
| `mean_judge_score` | 5.0000 | 3.6000 | 5.0000 |
| Quality checks | PASS | FAIL | PASS |
| Freshness | FRESH | STALE | FRESH |

Chuỗi bằng chứng chính là: corruption làm giảm tính hợp lệ/đầy đủ dữ liệu, khiến quality/freshness fail và các metric của agent giảm; repair từ raw snapshot khôi phục quality/freshness và toàn bộ metric về baseline.

## 7. Quyết định kỹ thuật và giới hạn

Quyết định quan trọng là dùng cùng một evaluation set cho cả ba trạng thái và repair từ raw snapshot thay vì sửa trực tiếp corrupted data. Cách này giúp so sánh metric công bằng và bảo toàn khả năng truy vết nguồn.

Quality Gate đã chạy thật bằng Great Expectations 1.x. Ragas chưa chạy trong lần xác minh này vì được thiết kế là bước tùy chọn chậm (`RUN_RAGAS=1`); các metric chính vẫn được tính và lưu trong `data/results/`.

## 8. Cam kết rà soát

- [ ] Đã tự rà soát nội dung báo cáo trước khi nộp.
- [ ] Đã đối chiếu mọi kết luận với artifact hoặc metric tương ứng.
- [ ] Báo cáo không chứa secret.

**Họ và tên:** Dương Xuân Vinh
**Ngày xác nhận:** 2026-09-25

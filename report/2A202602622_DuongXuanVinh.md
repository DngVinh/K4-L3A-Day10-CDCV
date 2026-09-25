# Member Role Report — Day 10: Data Pipeline & Data Observability

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

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Baseline orchestration | src/pipelines/phase1.py | Raw snapshot, clean schema và evaluation set | Baseline cleaned data, index, metrics, quality/freshness report | Hoàn thành |
| Corruption–repair integration | src/pipelines/corruption_flow.py | Baseline artifacts, raw snapshot và corruption scenarios | Corrupted/repaired data, metrics, quality reports và comparison report | Hoàn thành |
| Reproducibility/evidence | script/run_phase1.py, script/run_corruption_flow.py | Python 3.13.15 và dependencies | Lệnh chạy, logs, metrics và artifact evidence | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --- | --- | --- |
| Chuẩn hóa contract và đường dẫn artifact | TV1–TV4; ingestion, cleaning, evaluation, observability | Các flow dùng cùng schema/path/test set |
| Tích hợp và kiểm tra runtime | Great Expectations 1.x, Chroma, evaluation | Smoke test chạy được trên Python 3.13.15 |
| Tổng hợp tài liệu bằng chứng | Cả nhóm | Cập nhật phân công, report TV5 và các report/metrics của pipeline |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Điều phối baseline từ raw đến evaluation | src/pipelines/phase1.py | 24 records; retrieval hit rate 1.0000; quality PASS | script/run_phase1.py và data/reports/phase1_report.md |
| Điều phối corruption và repair | src/pipelines/corruption_flow.py | Corrupted giảm chất lượng; repaired khôi phục metrics | script/run_corruption_flow.py và data/reports/corruption_report.md |
| Tổng hợp metrics ba trạng thái | data/results/*_metrics.json | Baseline → corrupted → repaired: 1.0000 → 0.4000 → 1.0000 retrieval hit rate | data/results/ |
| Xác minh quality/freshness | data/quality/ | Baseline/repaired PASS + FRESH; corrupted FAIL + STALE | Quality reports và freshness reports |

Output tích hợp quan trọng là data/reports/corruption_report.md: report chứng minh corruption làm metric và quality signal giảm, sau đó repair từ raw snapshot khôi phục về baseline.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Pipeline phải chạy cùng một benchmark qua ba trạng thái baseline, corrupted và repaired. TV5 cần bảo đảm các trạng thái không dùng nhầm index hoặc evaluation set, đồng thời mọi kết luận trong report phải đối chiếu được với artifact thực tế.

### Cách triển khai

phase1.py tải raw records từ Crossref hoặc snapshot offline, tạo clean dataframe, chạy quality/freshness gate, build embedding/index, tạo hoặc đọc evaluation set, chạy evaluation và sinh baseline report. corruption_flow.py dùng baseline clean data để tạo sáu corruption scenarios, ghi corruption log, chạy quality/freshness và evaluation trên index corrupted, sau đó đọc lại raw snapshot, clean lại từ đầu, tạo index repaired và sinh comparison report.

Ba trạng thái dùng collection và manifest riêng: papers-baseline, papers-corrupted và papers-repaired. Repair không sửa trực tiếp dataframe corrupted mà rebuild từ data/raw/crossref_records.json.

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input | data/raw/crossref_records.json, clean schema và data/eval/test_set.json |
| Output | data/clean/, data/embeddings/, data/results/, data/quality/ và data/reports/ |
| Module phụ thuộc | Ingestion, cleaning, retrieval, evaluation và observability |
| Module sử dụng output | Comparison report, group report và các bước kiểm tra nộp bài |
| Điều kiện lỗi cần xử lý | Quality gate baseline/repair fail thì không publish index; corrupted được giữ để đo tác động |

### Cách xác minh

~~~powershell
$env:PYTHONPATH = 'src'
& '.\.venv-py313\Scripts\python.exe' script/run_phase1.py
& '.\.venv-py313\Scripts\python.exe' script/run_corruption_flow.py
~~~

- **Kết quả mong đợi:** Hai flow kết thúc với exit code 0; repaired quality/freshness và agent metrics trở về baseline.
- **Kết quả thực tế:** Baseline và corruption-repair đều exit code 0; baseline/repaired hit rate 1.0000, corrupted hit rate 0.4000.
- **Artifact/log:** data/reports/phase1_report.md, data/reports/corruption_report.md, data/results/ và data/quality/.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Cần so sánh công bằng ba trạng thái và chứng minh repair thực sự phục hồi dữ liệu.
- **Các phương án đã cân nhắc:**
  1. Sửa trực tiếp các giá trị corrupted trong dataframe hiện tại.
  2. Rebuild lại từ raw snapshot tin cậy và tạo index repaired riêng.
- **Phương án đã chọn:** Dùng cùng data/eval/test_set.json cho cả ba trạng thái; repair bằng cách rebuild từ raw snapshot; tách collection/index cho baseline, corrupted và repaired.
- **Lý do:** Cách này giữ nguyên benchmark, bảo toàn data lineage, tránh che lỗi bằng patch cục bộ và giúp tái lập kết quả trên máy khác.
- **Bằng chứng quyết định phù hợp:** Quality chuyển FAIL → PASS, freshness STALE → FRESH, retrieval hit rate 0.4000 → 1.0000, mean token F1 0.6529 → 1.0000.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Quality report chỉ có manual checks hoặc Great Expectations không khả dụng khi chạy trong runtime không tương thích.
- **Lệnh hoặc bước tái hiện:** Chạy pipeline bằng runtime không có Great Expectations 1.x rồi kiểm tra trường great_expectations.available trong data/quality/baseline_quality_report.json.
- **Nguyên nhân gốc:** Great Expectations 1.x và nhóm dependencies cần runtime Python tương thích; môi trường Python 3.14 ban đầu không bật được validation path đầy đủ.
- **Cách xử lý:** Cài Python 3.13.15, tạo .venv-py313, cài dependencies từ requirements.txt và chạy lại hai flow.
- **Cách xác minh sau khi sửa:** Baseline và repaired report có great_expectations.available=true và success=true; corrupted có available=true, success=false đúng như corruption kỳ vọng.
- **Điều học được:** Reproducibility phải bao gồm cả phiên bản Python, dependency và trạng thái của quality framework, không chỉ lệnh chạy.

## 7. Hiểu biết về luồng end-to-end

1. Dữ liệu đi từ Crossref đến vector index qua raw response/records, cleaning và data modeling; sau đó text_for_embedding được tạo, embedding được lưu vào manifest và Chroma index.
2. Evaluation set chứa câu hỏi, ground truth và ground_truth_doc_ids. Retrieval hit rate kiểm tra document đúng có nằm trong kết quả; token F1 và judge metrics đánh giá answer so với ground truth.
3. Quality checks kiểm tra tính hợp lệ, completeness và uniqueness của dataframe; freshness monitoring kiểm tra tuổi dữ liệu theo published, threshold 180 ngày và stale ratio tối đa 25%.
4. Cùng test set là bắt buộc để metric thay đổi phản ánh tác động của corruption/repair, không phải do benchmark khác nhau.
5. Repair thành công khi rebuilt data đạt quality PASS, freshness FRESH, index repaired được tạo và metrics khôi phục về baseline; trong run này cả bốn metric chính đều trở lại giá trị baseline.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| --- | ---: | ---: | ---: | --- |
| retrieval_hit_rate | 1.0000 | 0.4000 | 1.0000 | Corruption làm mất 60 điểm phần trăm; repair phục hồi toàn bộ |
| mean_token_f1 | 1.0000 | 0.6529 | 1.0000 | Answer overlap giảm rồi trở lại baseline |
| judge_accuracy | 1.0000 | 0.7000 | 1.0000 | 3/10 verdict heuristic bị ảnh hưởng ở corrupted; không phải LLM judge thực |
| mean_judge_score | 5.0000 | 3.4000 | 5.0000 | Mất 1.6 điểm rồi phục hồi; heuristic fallback |
| Quality checks | PASS | FAIL | PASS | GX phát hiện DOI trùng và summary ngắn |
| Freshness status | FRESH | STALE | FRESH | 7/23 stale rows tạo stale ratio 30,43% |

### Kết luận từ số liệu

1. Drop latest records, blank summary, duplicate rows và stale dates → summary/uniqueness/freshness signals fail → retrieval hit rate giảm 1.0000 xuống 0.4000 và token F1 giảm xuống 0.6529. Row count vẫn pass ngưỡng 5–5000.
2. Rebuild từ raw snapshot → quality/freshness trở lại PASS/FRESH → retrieval hit rate, token F1, judge accuracy và mean judge score đều phục hồi về baseline.

Corruption ảnh hưởng rõ nhất đến agent là drop_latest_records: 5 record mới nhất bị bỏ, trong đó có các document được dùng làm ground truth của evaluation set, nên retrieval hit rate giảm mạnh. duplicate_rows và blank_summary tạo tín hiệu quality rõ ràng; stale_date tạo tín hiệu freshness rõ ràng.

Kết quả khác kỳ vọng là không phải mọi corruption đều tạo một quality check riêng: noise có thể vẫn vượt ngưỡng độ dài summary và truncate title chưa có expectation kiểm tra độ dài title. Vì vậy cần đọc cả corruption log và agent metrics, không chỉ dựa vào một quality gate.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. Pipeline integration cần contract rõ cho input/output, identity, paths và evaluation set.
2. Observability phải kết hợp quality validity với freshness SLA; một pipeline có thể chạy không lỗi nhưng dữ liệu vẫn sai hoặc cũ.
3. RAG metrics phản ánh trực tiếp chất lượng dữ liệu/index, nên baseline–corrupted–repaired phải được đo trên cùng benchmark.

### Nếu có thêm thời gian

Bật RUN_RAGAS=1 để bổ sung answer relevancy, context precision, context recall và faithfulness; đồng thời chạy thử REFRESH_SOURCE=1 với raw snapshot mới và so sánh drift theo từng lần chạy.

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa .env, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Dương Xuân Vinh
**Ngày xác nhận:** 2026-09-25

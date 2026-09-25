# Báo cáo cá nhân — Thành viên 3: Data Observability

> Báo cáo này ghi nhận phần mã và kiểm thử đã hoàn thành trong repository hiện tại. Các chỉ số đánh giá RAG chỉ được điền sau khi nhóm chạy hai pipeline và tạo artifact thực tế.

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | **Đặng Quốc Cường** |
| MSSV | **2A202602466** |
| Khóa/Lớp | K4 — L3A - H201|
| Tên nhóm | **CDCV** |
| Vai trò chính | Thành viên 3 — Observability owner (nhóm 5 người) |
| Repository | **https://github.com/DngVinh/K4-L3A-Day10-CDCV** |
| Ngày cập nhật báo cáo | 2026-09-25 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Data Quality Gate | `src/observability/quality.py`: `run_data_quality_checks` | Cleaned hoặc corrupted `pandas.DataFrame`, `Settings`, tên trạng thái | Dictionary gồm `success`, các checks và freshness; JSON trong `data/quality/` | Đã triển khai, đã kiểm thử độc lập |
| Freshness SLA | `src/observability/quality.py`: `build_freshness_report` | DataFrame có `age_days` và `published`, `Settings`, đường dẫn báo cáo | JSON có khoảng ngày xuất bản, số/tỷ lệ bài cũ, `is_fresh` | Đã triển khai, đã kiểm thử độc lập |
| Báo cáo baseline | `src/observability/reporting.py`: `generate_phase1_report` | Tóm tắt nguồn, metrics, quality và freshness | `data/reports/phase1_report.md` khi pipeline gọi hàm | Đã triển khai, đã kiểm thử với dữ liệu mẫu |
| Báo cáo so sánh | `src/observability/reporting.py`: `generate_corruption_report` | Metrics của 3 trạng thái; quality và freshness của corrupted/repaired | `data/reports/corruption_report.md` khi pipeline gọi hàm | Đã triển khai, đã kiểm thử với dữ liệu mẫu |

Trong phương án nhóm 5 người tại `report/README.md`, thành viên 2 phụ trách clean data và test set; thành viên 4 phụ trách corruption; thành viên 5 phụ trách tích hợp pipeline. Phần của tôi nhận DataFrame và metrics từ các bước đó, rồi trả tín hiệu chất lượng và tạo báo cáo cho luồng tích hợp.

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Module được hỗ trợ | Kết quả |
| --- | --- | --- |
| Viết kiểm thử độc lập | `quality.py`, `reporting.py` | `tests/test_observability.py` xác minh dữ liệu sạch, các lỗi dữ liệu, freshness và nội dung báo cáo; 2 bài kiểm tra đạt |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/artifact | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Cài Quality Gate bằng Great Expectations 1.x | `src/observability/quality.py` | 6 checks: số dòng 5–5000; 3 cột không null; `paper_id` duy nhất; `summary` dài tối thiểu 30 ký tự | `tests/test_observability.py::test_quality_gate_detects_corruption_and_freshness` |
| Giám sát độ tươi | `src/observability/quality.py` | Đếm bài có `age_days > 180`; `is_fresh=False` nếu tỷ lệ bài cũ vượt 25%, có tuổi không xác định hoặc tập dữ liệu rỗng | Cùng bài kiểm tra trên: 3/5 bài cũ cho `stale_ratio=0.6`, `is_fresh=False` |
| Sinh báo cáo Markdown | `src/observability/reporting.py` | Bảng metrics, quality, freshness và chênh lệch so với baseline | `tests/test_observability.py::test_reports_render_supplied_values` |

Kết quả kiểm thử là dữ liệu **giả lập trong thư mục tạm**, không phải metrics RAG thực của nhóm. Hiện `data/quality/`, `data/results/` và `data/reports/` chưa có artifact chạy pipeline để đưa số liệu thật vào báo cáo này.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Pipeline RAG có thể tiếp tục chạy khi dữ liệu đầu vào bị trùng, thiếu nội dung hoặc quá cũ. Quality Gate phát hiện lỗi cấu trúc/nội dung trước khi dữ liệu được dùng để index; Freshness SLA phát tín hiệu riêng về độ mới. Báo cáo Markdown giúp nhóm đối chiếu tín hiệu dữ liệu với các chỉ số đánh giá Agent.

### Cách triển khai

`run_data_quality_checks` tạo GX 1.x ephemeral context, Pandas data source, DataFrame asset và batch. Trước khi kiểm định, hàm chuẩn hóa khoảng trắng và chuyển chuỗi rỗng ở các trường bắt buộc thành null trên **bản sao** của DataFrame. Hàm chạy từng expectation, trả kết quả pass/fail và ghi JSON theo tên trạng thái vào `data/quality/`.

Freshness dùng `age_days` nếu cột này có sẵn; nếu không, tính tuổi từ `published`. Hàm đếm bài quá ngưỡng 180 ngày và tính tỷ lệ trên tổng số dòng. Tuổi không xác định được xem là tín hiệu không an toàn. Hai hàm reporting nhận số liệu từ pipeline, tạo bảng Markdown và tính chênh lệch metrics giữa corrupted/repaired với baseline; chúng không tự khẳng định đã phục hồi khi thiếu bằng chứng.

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input chất lượng | DataFrame có `paper_id`, `title`, `text_for_embedding`, `summary`; freshness dùng thêm `age_days` hoặc `published` |
| Output chất lượng | Dictionary/JSON gồm `report_name`, `success`, `checks`, `freshness` |
| Output freshness | JSON gồm `latest_published`, `oldest_published`, `stale_rows`, `unknown_age_rows`, `total_rows`, `stale_ratio`, `is_fresh` và các ngưỡng |
| Input báo cáo | `source_summary`, metrics như `retrieval_hit_rate`, `mean_token_f1`, `judge_accuracy`, `mean_judge_score`, quality và freshness |
| Output báo cáo | Markdown tại `settings.paths.baseline_report` và `settings.paths.comparison_report` khi pipeline tích hợp gọi hàm |
| Module phụ thuộc | `core.config`, `core.utils`, Pandas, Great Expectations 1.x; dữ liệu sạch từ thành viên 2 |
| Module sử dụng output | `src/pipelines/phase1.py` và `src/pipelines/corruption_flow.py` do thành viên 5 tích hợp |
| Điều kiện lỗi cần xử lý | Bản ghi trùng, cột bắt buộc null/chuỗi trắng, tóm tắt ngắn, bài cũ quá tỷ lệ cho phép, tuổi không xác định |

### Cách xác minh

```powershell
$env:PYTHONPATH='src'
python -m pytest tests/test_observability.py -q --tb=line
```

- **Kết quả mong đợi:** Dữ liệu sạch pass; dữ liệu có DOI trùng, title trắng, summary rỗng và tỷ lệ bài cũ 60% bị phát hiện; báo cáo chứa đúng số liệu đầu vào.
- **Kết quả thực tế:** `2 passed in 2.31s` trong lần kiểm tra gần nhất.
- **Artifact kiểm thử:** `tests/test_observability.py`; các JSON/Markdown của bài kiểm tra được tạo trong thư mục tạm của pytest.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Chuỗi chỉ gồm khoảng trắng có thể không bị GX `ExpectColumnValuesToNotBeNull` xem là null.
- **Các phương án đã cân nhắc:** Kiểm tra thêm bằng Pandas sau GX; hoặc chuẩn hóa chuỗi trước khi đưa DataFrame vào GX.
- **Phương án đã chọn:** Chuẩn hóa trên bản sao DataFrame, đổi chuỗi rỗng ở các cột bắt buộc thành null rồi chạy GX.
- **Lý do:** Giữ toàn bộ tín hiệu chất lượng trong kết quả expectation, đồng thời không làm thay đổi DataFrame của pipeline.
- **Bằng chứng:** Kiểm thử đặt `title="  "` và xác nhận `ExpectColumnValuesToNotBeNull` thất bại.

## 6. Một lỗi đã xử lý

- **Triệu chứng:** Lần chạy đầu báo `AttributeError: module 'great_expectations' has no attribute 'ExpectTableRowCountToBeBetween'`.
- **Bước tái hiện:** Chạy bài kiểm tra `test_quality_gate_detects_corruption_and_freshness` với Great Expectations 1.23.1.
- **Nguyên nhân gốc:** Các lớp expectation không được export trực tiếp ở namespace gốc `great_expectations` của phiên bản đã cài.
- **Cách xử lý:** Import các lớp từ `great_expectations.expectations`, giữ API context/data source/batch theo GX 1.x.
- **Cách xác minh sau khi sửa:** Chạy lại lệnh pytest ở mục 4; kết quả `2 passed`.
- **Điều học được:** Cần kiểm tra API của phiên bản thư viện thực tế, nhất là vị trí import của các lớp expectation.

## 7. Hiểu biết về luồng end-to-end

1. Crossref API hoặc snapshot tạo raw records. Cleaning chuẩn hóa DOI, văn bản, ngày tháng và `text_for_embedding`; Quality Gate kiểm tra DataFrame trước khi thành viên phụ trách retrieval tạo embedding và nạp ChromaDB.
2. Evaluation set chứa câu hỏi, đáp án chuẩn và `ground_truth_doc_ids`. Retrieval hit đo việc truy xuất đúng tài liệu; Token F1 và LLM Judge đánh giá câu trả lời so với đáp án chuẩn.
3. Quality checks đo tính hợp lệ, đầy đủ, duy nhất và độ dài nội dung. Freshness đo riêng tỷ lệ bài báo quá 180 ngày, cảnh báo khi vượt 25%.
4. Cùng một test set giúp khác biệt giữa baseline, corrupted và repaired phản ánh thay đổi dữ liệu/pipeline thay vì thay đổi đề kiểm tra.
5. Repair cần được đối chiếu bằng clean/repaired artifacts, quality và freshness signals, cùng `baseline_metrics.json`, `corrupted_metrics.json`, `repaired_metrics.json`; không kết luận phục hồi chỉ vì lệnh chạy xong.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | Chưa có | Chưa có | Chưa có | Chờ 3 metrics JSON của pipeline |
| `mean_token_f1` | Chưa có | Chưa có | Chưa có | Chờ 3 metrics JSON của pipeline |
| `judge_accuracy` | Chưa có | Chưa có | Chưa có | Chờ 3 metrics JSON của pipeline |
| `mean_judge_score` | Chưa có | Chưa có | Chưa có | Chờ 3 metrics JSON của pipeline |
| Quality checks | Test mẫu: PASS | Test mẫu: FAIL | Chưa chạy pipeline | Test mẫu phát hiện DOI trùng, title trắng, summary rỗng |
| Freshness status | Test mẫu: PASS | Test mẫu: FAIL | Chưa chạy pipeline | Test mẫu corrupted có 3/5 bài quá 180 ngày |

### Kết luận từ bằng chứng hiện có

- Với dữ liệu kiểm thử giả lập, corruption làm Quality Gate báo fail và Freshness SLA chuyển sang `is_fresh=False`. Bài kiểm tra **không đo Agent**, nên chưa kết luận được mức ảnh hưởng lên Hit Rate hoặc Token F1.
- Chưa có repaired artifacts và metrics thực; chưa thể khẳng định luồng repair đã phục hồi chất lượng Agent. Sau khi thành viên 5 chạy pipeline, cần đối chiếu cùng test set và điền số liệu của ba trạng thái vào bảng trên.
- Trong các lỗi đã thử, DOI trùng, title trắng và summary rỗng đều được GX phát hiện. Chưa thể xếp hạng lỗi nào ảnh hưởng RAG rõ nhất khi chưa có kết quả đánh giá từng kịch bản.

## 9. Điều học được và hướng cải thiện

1. Contract của DataFrame và artifact cần thống nhất giữa cleaning, observability và pipeline; tên cột sai có thể làm hỏng kiểm định hoặc báo cáo.
2. Quality Gate và Freshness SLA cần hai tín hiệu rõ ràng: dữ liệu có thể đủ trường nhưng vẫn quá cũ.
3. Tác động tới RAG phải được chứng minh bằng metrics trên cùng test set; cảnh báo dữ liệu tự nó chưa chứng minh câu trả lời Agent đã sai.

Nếu có thêm thời gian, tôi sẽ bổ sung kiểm thử tích hợp trên clean/corrupted/repaired artifacts thực sau khi hai pipeline hoàn thiện, rồi xác minh báo cáo Markdown khớp với từng file JSON nguồn.

## 10. Cam kết của thành viên

- [x] Báo cáo nêu đúng phần mã và bài kiểm tra đã hoàn thành, tách khỏi phần pipeline chưa chạy.
- [x] Các kết luận hiện tại dựa trên bài kiểm tra và không dùng metrics giả lập làm kết quả RAG của nhóm.
- [x] Báo cáo không chứa API key, token hoặc nội dung `.env`.
- [x] Bổ sung họ tên, MSSV, tên nhóm, URL repository và xác nhận của bản thân.
- [ ] Chạy pipeline tích hợp, điền metrics thật và rà soát lại toàn bộ bảng kết quả trước khi nộp.

**Họ và tên:** Đặng Quốc Cường

**Ngày xác nhận:** 2026-09-25

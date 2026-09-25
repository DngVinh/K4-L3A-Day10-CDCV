# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Nguyễn Anh Dũng |
| MSSV | 2A202602554 |
| Khóa/Lớp | K4 |
| Tên nhóm | CDCV |
| Vai trò chính | Thành viên 4 — Corruption & Repair Owner |
| Repository | https://github.com/DngVinh/K4-L3A-Day10-CDCV |
| Ngày hoàn thành | 2026-09-25 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Data corruption suite | `src/ingestion/corruption.py` — `corrupt_clean_dataframe()` | Cleaned dataframe từ `cleaning.py` | Corrupted dataframe, `text_for_embedding` được tạo lại và `corruption_log.json` | Hoàn thành |
| Kiểm tra corruption/repair | Đối chiếu corrupted và repaired dataset | Corrupted dataset, repaired dataset và log | Kết luận dữ liệu repair có hợp lệ hay không | Đã tích hợp, đã đối chiếu |

Phạm vi chính của tôi là tạo các lỗi dữ liệu có chủ đích, ghi nhận đầy đủ bằng log và kiểm tra kết quả sau khi pipeline repair chạy. Tôi không nhận ownership cho bước làm sạch, đánh giá metric hoặc orchestration toàn bộ pipeline.

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --- | --- | --- |
| Thống nhất contract dữ liệu | Thành viên 2 / `cleaning.py` | Xác định input tối thiểu cho corruption gồm `paper_id`, `title`, `summary`, `published`, `authors_joined`, `categories_joined`. |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Triển khai 6 kịch bản corruption | `src/ingestion/corruption.py` | Corrupted dataset từ 24 dòng clean thành 23 dòng corrupted | Artifact thật có đủ 6 scenario trong log. |
| Tạo lại ngữ cảnh embedding | `_rebuild_embedding_text()` | Cột `text_for_embedding` đồng bộ với các trường đã bị làm bẩn | Toàn bộ 23 dòng đầu ra bắt đầu bằng `Title:`. |
| Ghi audit log | `core.utils.write_json()` | `data/results/corruption_log.json` có số dòng, loại lỗi, số lượng và `paper_id` bị ảnh hưởng | Log ghi 5 bản ghi bị xóa; các scenario tiếp theo tác động 4, 4, 4, 6 và 4 dòng. |

Output cụ thể phần việc của tôi là hàm `corrupt_clean_dataframe()`. Hàm không sửa dataframe đầu vào, trả về dataframe đã bị làm bẩn có thể tái lập và tạo log chi tiết để phục vụ quality check, evaluation và báo cáo.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Pipeline cần mô phỏng sự cố dữ liệu để chứng minh dữ liệu xấu làm giảm chất lượng retrieval/RAG, đồng thời kiểm tra khả năng repair từ nguồn raw đáng tin cậy.

### Cách triển khai

Hàm tạo bản sao sâu của cleaned dataframe để không thay đổi baseline. Hàm lần lượt xóa 20% bản ghi mới nhất, làm rỗng summary, thêm chuỗi nhiễu, cắt title còn tối đa 7 ký tự, lùi ngày xuất bản 365 ngày và sao chép một số dòng để tạo duplicate. Mỗi nhóm bản ghi được chọn bằng seed cố định; cùng input sẽ tạo cùng kết quả. Cuối cùng hàm tạo lại `text_for_embedding` và ghi audit log JSON.

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input | Dataframe sạch có `paper_id`, `title`, `summary`, `published`, `authors_joined`, `categories_joined`. |
| Output | Dataframe corrupted và `data/results/corruption_log.json`. |
| Module phụ thuộc | `core.utils.write_json`; dữ liệu sạch do `src/ingestion/cleaning.py` tạo. |
| Module sử dụng output | `src/pipelines/corruption_flow.py`, quality check, evaluation và reporting. |
| Điều kiện lỗi cần xử lý | Dataset rỗng hoặc thiếu cột bắt buộc sẽ báo `ValueError`. |

### Cách xác minh

```bash
.venv/bin/python -m compileall -q src/ingestion/corruption.py
```

- **Kết quả mong đợi:** Module hợp lệ; khi gọi với cleaned dataframe, log có đủ 6 scenario.
- **Kết quả thực tế:** Compile thành công; từ 24 dòng clean tạo 23 dòng corrupted. Log ghi 4 lượt blank summary, 4 lượt inject noise, 4 lượt truncate title, 6 lượt stale date và 4 lượt duplicate; các nhóm có thể chồng lắp. Kiểm tra trên output thấy 5 summary dưới 30 ký tự và 4 DOI trùng; `text_for_embedding` được tạo lại cho mọi dòng.
- **Artifact/log:** `data/clean/papers_clean_corrupted.csv`, `data/clean/papers_clean_corrupted.json` và `data/results/corruption_log.json`.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Corruption cần đủ rõ để quality gate và RAG evaluation phát hiện, nhưng vẫn có thể tái hiện để so sánh công bằng.
- **Các phương án đã cân nhắc:** Chọn ngẫu nhiên hoàn toàn mỗi lần chạy; hoặc chọn với seed cố định.
- **Phương án đã chọn:** Dùng seed cố định riêng cho từng scenario.
- **Lý do:** Kết quả có thể tái lập, dễ debug và cho phép so sánh baseline/corrupted/repaired trên cùng điều kiện.
- **Bằng chứng:** Artifact thật có log đủ 6 scenario và liệt kê chính xác các `paper_id` bị tác động; cùng input sẽ chọn cùng record.

## 6. Blocker đã xử lý khi tích hợp

- **Phạm vi bị ảnh hưởng:** Kiểm tra repaired dataset và freshness sau corruption.
- **Nguyên nhân ban đầu:** Repair flow chưa có artifact lúc viết bản báo cáo đầu; sau tích hợp phát hiện `stale_date` chưa đồng bộ `age_days` và tỷ lệ bản ghi cũ chưa vượt SLA.
- **Cách xử lý:** Flow đã tạo repaired data từ raw; scenario stale date cập nhật tuổi và chọn đủ bản ghi để vượt ngưỡng 25%.
- **Xác minh:** Baseline/corrupted/repaired có 24/23/24 dòng; repaired JSON bằng baseline JSON; freshness FRESH → STALE → FRESH.

## 7. Hiểu biết về luồng end-to-end

1. Crossref cung cấp raw response và raw records; cleaning chuẩn hóa thành dataset sạch, sau đó RAG tạo embedding MiniLM và nạp ChromaDB vector index.
2. Evaluation set chứa câu hỏi, ground truth và `ground_truth_doc_ids`; retrieval hit đo việc tài liệu đúng xuất hiện trong kết quả truy xuất, còn câu trả lời được đo bằng Token F1/judge.
3. Quality checks kiểm tra null, duplicate, độ dài; freshness monitoring đánh giá độ mới bằng `age_days` và ngưỡng SLA.
4. Ba trạng thái phải dùng cùng test set để biến động metric phản ánh thay đổi dữ liệu, không phải do thay đổi câu hỏi.
5. Repair thành công khi repaired artifact hợp lệ, quality/freshness phù hợp và metric phục hồi gần hoặc bằng baseline.

## 8. Phân tích kết quả

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 1,0000 | 0,4000 | 1,0000 | 5 DOI bị xóa thuộc ground truth của các câu miss |
| `mean_token_f1` | 1,0000 | 0,6529 | 1,0000 | Giảm rồi phục hồi trên cùng test set |
| `judge_accuracy` | 1,0000 | 0,7000 | 1,0000 | Heuristic fallback, không phải LLM judge thực |
| `mean_judge_score` | 5,0000 | 3,4000 | 5,0000 | Heuristic fallback, thang 1–5 |
| Quality checks | PASS | FAIL | PASS | Duplicate và summary ngắn bị phát hiện |
| Freshness status | FRESH | STALE | FRESH | 1/24 → 7/23 → 1/24 dòng stale |

Sau tích hợp ngày 2026-09-25, sáu kịch bản chạy đồng thời làm quality/freshness đổi PASS/FRESH → FAIL/STALE và hit rate giảm 1,0000 → 0,4000. Repair từ raw đưa clean data, quality/freshness và bốn metric về baseline. Không thể quy toàn bộ tác động cho một scenario nếu chưa chạy từng lỗi riêng.

## 9. Điều học được và hướng cải thiện

1. Corruption phải được log theo record và có thể tái lập thì kết quả đánh giá mới có thể kiểm chứng.
2. Thay đổi summary mà không tạo lại `text_for_embedding` sẽ khiến index nhận dữ liệu cũ, làm thí nghiệm không phản ánh đúng lỗi dữ liệu.
3. Quality gate hiện phát hiện duplicate và summary rỗng/ngắn; title ngắn cần bổ sung expectation riêng.

Nếu có thêm thời gian, tôi sẽ bổ sung test tự động cho từng scenario và kiểm tra bất biến của repair: repaired dataframe phải khớp với dataset tái tạo từ raw theo schema và số lượng dòng kỳ vọng.

## 10. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Anh Dũng

**Ngày xác nhận:** 2026-09-25

# Báo cáo nhóm CDCV — Day 10: Data Pipeline & Data Observability

## 1. Thông tin bài nộp

| Thông tin | Nội dung |
| --- | --- |
| Khóa/lớp | K4-L3-DAY10 |
| Nhóm | CDCV |
| Repository | [K4-L3A-Day10-Data-Pipeline-Data-Observability](https://github.com/DngVinh/K4-L3A-Day10-Data-Pipeline-Data-Observability) |
| Ngày tổng hợp | 2026-09-25 |
| Email liên hệ | tendangc@gmail.com |

| STT | Thành viên | MSSV | Phần việc chính | Báo cáo cá nhân |
| ---: | --- | --- | --- | --- |
| 1 | Đào Quang Cảnh | 2A202602542 | Nguồn Crossref, raw snapshot, `src/ingestion/crossref.py` | [daoquangcanh.md](daoquangcanh.md) |
| 2 | Trần Cao Thắng | 2A202602520 | Cleaning, data contract, evaluation set | [2A202602520_TranCaoThang.md](2A202602520_TranCaoThang.md) |
| 3 | Đặng Quốc Cường | 2A202602466 | Great Expectations, freshness, báo cáo | [dangquoccuong_report.md](dangquoccuong_report.md) |
| 4 | Nguyễn Anh Dũng | 2A202602554 | Sáu kịch bản corruption, repair | [2A202602554-NguyenAnhDung.md](2A202602554-NguyenAnhDung.md) |
| 5 | Dương Xuân Vinh | 2A202602622 | Trưởng nhóm, tích hợp hai pipeline và bằng chứng | [2A202602622_DuongXuanVinh.md](2A202602622_DuongXuanVinh.md) |

## 2. Tóm tắt kết quả

Nhóm đã hoàn thiện luồng đọc snapshot Crossref, chuẩn hóa 24 bài báo, kiểm định bằng Great Expectations, tạo embedding và index ChromaDB, đánh giá 10 câu hỏi, tiêm sáu dạng lỗi rồi tái tạo dữ liệu từ raw snapshot. Ngày 2026-09-25, hai pipeline chạy lại thành công bằng môi trường `.venv`; clean data, test set, ba index, metrics, quality/freshness và báo cáo được sinh lại từ source hiện tại. Baseline có retrieval hit rate và token F1 đều bằng 1,0000; sau corruption lần lượt còn 0,4000 và 0,6529; sau repair trở lại 1,0000. Quality gate chuyển PASS → FAIL → PASS và freshness chuyển FRESH → STALE → FRESH. Việc bỏ 5 bài mới nhất tác động trực tiếp tới retrieval vì cả 5 là ground truth của các câu bị trượt. Sáu lỗi được tiêm đồng thời nên không thể quy toàn bộ suy giảm cho riêng lỗi này. Cả 30 lượt judge dùng heuristic dự phòng, không phải LLM thực; Ragas không chạy. Bốn test tự động đạt. Các artifact vừa sinh và báo cáo cá nhân vẫn cần được rà soát, commit và đẩy lên nhánh nộp bài.

## 3. Kiến trúc và phân công đầu ra

```text
data/raw/crossref_response.json hoặc Crossref REST API
  → parse và lưu raw records → clean DataFrame
  → quality gate + freshness → MiniLM embedding + ChromaDB
  → test set cố định → baseline answers/metrics
  → sáu lỗi đồng thời → corrupted index/answers/metrics + quality/freshness
  → clean lại từ raw records → repaired index/answers/metrics
  → báo cáo so sánh ba trạng thái
```

| Khối | Input và xử lý | Output | Owner |
| --- | --- | --- | --- |
| Ingestion | Snapshot `message.items` hoặc Crossref `/works`; parse DOI, tiêu đề, abstract, tác giả, ngày; live mode retry tối đa 3 lần, fallback về snapshot | `data/raw/crossref_response.json`, `data/raw/crossref_records.json` | TV1 |
| Cleaning | Raw records; bỏ HTML, chuẩn hóa whitespace, DOI và ngày; lọc bản ghi thiếu trường thiết yếu, summary ngắn, DOI trùng | `data/clean/papers_clean.csv` và `.json` khi chạy | TV2 |
| Evaluation set | 10 bản ghi sạch mới nhất; câu hỏi summary, authors, date, categories và DOI làm ground truth | `data/eval/test_set.json` khi chạy | TV2 |
| Quality/freshness | Clean/corrupted/repaired DataFrame; sáu expectation GX và SLA tuổi tài liệu | `data/quality/` | TV3 |
| Embedding/retrieval | `text_for_embedding`; MiniLM + Chroma, ba collection riêng; tra cứu title chính xác và vector top 4 | `data/embeddings/`, `data/chroma/` khi chạy | TV5 tích hợp |
| Corruption/repair | Clean DataFrame; tiêm sáu lỗi, sau đó clean lại từ raw snapshot | `data/results/corruption_log.json`, dữ liệu repaired khi chạy | TV4, TV5 |
| Orchestration/report | Chạy baseline rồi corrupted và repaired trên cùng test set; tổng hợp metrics | `data/results/`, `data/reports/` | TV5, TV3 |

Code điều phối nằm tại [phase1.py](../src/pipelines/phase1.py) và [corruption_flow.py](../src/pipelines/corruption_flow.py). Baseline dừng trước khi tạo index nếu quality gate fail. Repair cũng kiểm tra quality gate trước khi xuất index repaired; corrupted được index riêng để đo hậu quả.

## 4. Cấu hình và cách tái hiện

| Cấu hình | Giá trị trong source hiện tại |
| --- | --- |
| Chế độ nguồn mặc định | Snapshot offline; chỉ gọi API khi `REFRESH_SOURCE=1` |
| Crossref query khi refresh | `agentic retrieval augmented generation large language model` |
| Crossref filter khi refresh | `from-pub-date:<ngày chạy - 180 ngày>,has-abstract:true` |
| Số bản ghi yêu cầu | 24 |
| Embedding | `sentence-transformers/all-MiniLM-L6-v2` |
| Chroma collections | `papers-baseline`, `papers-corrupted`, `papers-repaired` |
| Retrieval `top_k` | 4 |
| Freshness | Quá 180 ngày; tối đa 25% bản ghi cũ, không có tuổi không xác định |
| LLM trong lần chạy này | `LLM_PROVIDER=mock`; câu trả lời QA được trích từ metadata, judge dùng heuristic fallback |
| Ragas | Không chạy (`RUN_RAGAS=0`) |

Từ thư mục gốc repository trên Windows PowerShell, dùng `.venv` đã cài theo `pyproject.toml` rồi chạy:

```powershell
$env:PYTHONPATH='src'
$env:PYTHONIOENCODING='utf-8'
$env:LLM_PROVIDER='mock'
$env:RUN_RAGAS='0'
& .\.venv\Scripts\python.exe -m pytest -q
& .\.venv\Scripts\python.exe script/run_phase1.py
& .\.venv\Scripts\python.exe script/run_corruption_flow.py
```

Môi trường mới có thể tạo bằng `python -m venv .venv`, `.venv/Scripts/python.exe -m pip install -e .` và `.venv/Scripts/python.exe -m pip install pytest`. Với `LLM_PROVIDER=mock`, cả 30 lượt judge ghi `Fallback heuristic judge used because the LLM evaluator was unavailable.` Không đưa API key vào source hoặc báo cáo.

| Kiểm tra trên checkout này, 2026-09-25 | Kết quả | Bằng chứng |
| --- | --- | --- |
| Smoke test import bằng `.venv` | Thành công | `chromadb`, `great_expectations`, `sentence_transformers` |
| `pytest -q` bằng `.venv` | 4 passed | `tests/test_observability.py`, `tests/test_pipeline_contracts.py` |
| Baseline bằng `.venv`, `LLM_PROVIDER=mock` | Exit 0; 24 records; hit rate 1,0000; token F1 1,0000 | Clean dataset, test set, index, quality, answers và report |
| Corruption/repair bằng cùng `.venv` | Exit 0; 24 → 23 corrupted → 24 repaired; hit rate 1,0000 → 0,4000 → 1,0000 | Quality PASS → FAIL → PASS; freshness FRESH → STALE → FRESH |

Bảng số liệu ở mục 7–10 lấy từ artifact vừa sinh trên branch hiện tại; thay đổi vẫn cần commit và push.

## 5. Ingestion, cleaning và data contract

Snapshot [crossref_response.json](../data/raw/crossref_response.json) có 24 `message.items`; [crossref_records.json](../data/raw/crossref_records.json) có 24 bản ghi đã parse. Snapshot không lưu thời điểm lấy dữ liệu hoặc tham số truy vấn, nên không thể xác nhận lúc nào và bằng query nào nó được thu thập. Trong chế độ live, code gọi `https://api.crossref.org/works`, chỉ lưu response mới sau khi parse thành công; khi lỗi hoặc hết retry, nó dùng snapshot cũ.

| Trường | Raw → clean | Quy tắc và ý nghĩa |
| --- | --- | --- |
| `paper_id` | DOI → chuỗi lowercase | ID tài liệu và khóa deduplicate; thiếu thì bỏ bản ghi |
| `title` | Chuỗi → chuỗi đã bỏ HTML/khoảng trắng thừa | Thiếu thì bỏ bản ghi; cũng là khóa lookup theo tiêu đề |
| `summary` | Abstract → chuỗi sạch | Yêu cầu ít nhất 30 ký tự |
| `authors`, `categories` | Danh sách → danh sách đã chuẩn hóa và trường `*_joined` | Bỏ phần tử rỗng/trùng; dùng trong câu trả lời và embedding |
| `published`, `updated` | Ngày nguồn → ISO `YYYY-MM-DD` | Thiếu `published` thì bỏ bản ghi; `age_days` tính theo ngày chạy UTC |
| `text_for_embedding` | Tạo từ title, authors, published, categories, summary | Nội dung nạp vào Chroma; document ID dùng `paper_id` kèm vị trí dòng |

Đối chiếu raw snapshot bằng `build_clean_dataframe` với ngày 2026-09-25 cho **24 raw → 24 clean**, không bản ghi bị loại, không DOI trùng, không summary dưới 30 ký tự. Dữ liệu sạch được sắp theo ngày xuất bản mới nhất rồi theo DOI. `age_days` thay đổi theo ngày chạy; muốn đối chiếu đúng snapshot cũ phải giữ cùng ngày tham chiếu.

## 6. Thiết lập evaluation

`src/evaluation/testset.py` tạo 10 câu từ 10 bản ghi mới nhất, xoay vòng 4 `question_type`: `summary` (3), `authors` (3), `date` (2), `categories` (2). Mỗi câu lưu `id`, `question`, `ground_truth`, `ground_truth_doc_ids` là DOI của paper gốc. Pipeline baseline tạo test set nếu chưa có file; flow corruption đọc lại cùng đường dẫn cho corrupted và repaired. Trong ba file `*_answers.json` đã lưu, 10 `id`, câu hỏi và ground-truth ID khớp nhau giữa các trạng thái.

`retrieval_hit_rate` là tỷ lệ câu có DOI chuẩn trong top 4. `mean_token_f1` đo chồng lắp token giữa đáp án và câu trả lời. `judge_accuracy` và `mean_judge_score` trong artifact là từ **heuristic fallback** khi LLM judge không dùng được. Ragas được ghi `skipped`. Hàm QA hiện tại ưu tiên lookup theo tiêu đề được trích từ câu hỏi rồi mới dùng kết quả vector; vì vậy điểm baseline rất cao không đại diện cho một bài toán truy xuất ngữ nghĩa mù tiêu đề.

## 7. Kết quả baseline và artifact

| Artifact | Trạng thái trên branch hiện tại | Ghi chú |
| --- | --- | --- |
| `data/raw/crossref_response.json`, `crossref_records.json` | Có | 24 items/records |
| `data/clean/papers_clean*.csv` và `.json` | Đã sinh, chưa commit | Baseline 24, corrupted 23, repaired 24 dòng |
| `data/embeddings/`, `data/chroma/` | Đã sinh, chưa commit | Ba manifest dùng đường dẫn tương đối `data/chroma`; ba collection Chroma |
| `data/eval/test_set.json` | Đã sinh, chưa commit | 10 câu, dùng chung cho ba trạng thái |
| `data/results/*_metrics.json`, `*_answers.json` | Đã sinh lại, chưa commit | 10 câu mỗi trạng thái; metrics tính lại từ answers khớp JSON |
| `data/quality/`, `data/reports/` | Đã sinh lại, chưa commit | Quality/freshness JSON và hai Markdown report khớp lần chạy mới |

| Metric baseline | Giá trị | Diễn giải |
| --- | ---: | --- |
| `retrieval_hit_rate` | 1,0000 | 10/10 DOI chuẩn xuất hiện trong kết quả truy xuất |
| `mean_token_f1` | 1,0000 | 10/10 câu trả lời khớp ground truth theo phép đo đã lưu |
| `judge_accuracy` | 1,0000 | 10/10 đúng theo heuristic fallback |
| `mean_judge_score` | 5,0000 | Điểm trung bình heuristic trên thang 1–5 |
| Ragas | Không chạy | Metrics JSON ghi `skipped` |

Nguồn: [baseline_metrics.json](../data/results/baseline_metrics.json), [baseline_answers.json](../data/results/baseline_answers.json), [phase1_report.md](../data/reports/phase1_report.md).

## 8. Data quality và freshness

Code hiện tại dùng GX 1.x với 6 expectation: số dòng 5–5000; `paper_id`, `title`, `text_for_embedding` không null; `paper_id` duy nhất; `summary` dài ít nhất 30 ký tự. Trước khi kiểm tra, code trim chuỗi trên bản sao DataFrame. Quality gate chỉ phản ánh các quy tắc này: nó không có expectation riêng cho noise trong summary, title ngắn hoặc ngày quá cũ. Freshness được báo riêng.

| Check trong quality JSON và clean data mới | Ngưỡng | Baseline | Corrupted | Repaired |
| --- | --- | --- | --- | --- |
| Row count | 5–5000 | PASS, 24 | PASS, 23 | PASS, 24 |
| `paper_id`/`title`/`text_for_embedding` not null | 0 lỗi | PASS, 0 | PASS, 0 | PASS, 0 |
| `paper_id` unique | 0 DOI trùng | PASS, 0 | FAIL, 4 | PASS, 0 |
| `summary` min length | ≥30 ký tự | PASS, 0 | FAIL, 5 | PASS, 0 |
| Quality gate tổng | Tất cả pass | PASS | FAIL | PASS |

| Freshness JSON mới | Baseline | Corrupted | Repaired |
| --- | ---: | ---: | ---: |
| Latest published | 2026-07-22 | 2026-06-10 | 2026-07-22 |
| Oldest published | 2026-03-28 | 2025-05-20 | 2026-03-28 |
| Bản ghi quá 180 ngày | 1/24 | 7/23 | 1/24 |
| Tỷ lệ stale | 4,17% | 30,43% | 4,17% |
| Ngưỡng tối đa | 25% | 25% | 25% |
| Trạng thái | FRESH | STALE | FRESH |

Nguồn: [baseline quality](../data/quality/baseline_quality_report.json), [corrupted quality](../data/quality/corrupted_quality_report.json), [repaired quality](../data/quality/repaired_quality_report.json) và các file freshness trong `data/quality/`.

## 9. Corruption và repair

[corruption_log.json](../data/results/corruption_log.json) của lần chạy mới ghi **24 dòng đầu vào, 23 dòng đầu ra** và sáu scenario dưới đây. Các nhóm paper có thể chồng lắp; tổng số `count` không phải số paper riêng biệt.

| Kịch bản trong log | Bản ghi tác động | Tín hiệu quan sát và cách repair |
| --- | ---: | --- |
| `drop_latest_records` | 5 | Bỏ 5 bài mới nhất; cả 5 là ground truth của 5 câu bị miss; repair đưa chúng trở lại từ raw |
| `blank_summary` | 4 | Góp phần làm `summary_min_length` fail; repair đọc lại abstract gốc |
| `inject_noise` | 4 | Thêm nhiễu vào summary; quality gate hiện không kiểm tra noise trực tiếp |
| `truncate_title` | 4 | Title rút xuống dưới 8 ký tự; expectation hiện chỉ kiểm tra null, không kiểm tra độ dài title |
| `stale_date` | 6 | Lùi ngày xuất bản 365 ngày và cập nhật `age_days`; freshness vượt ngưỡng 25% |
| `duplicate_rows` | 4 | DOI trùng; uniqueness check fail |

Flow repair đọc `data/raw/crossref_records.json`, clean lại, chạy quality gate và tạo collection Chroma riêng trước khi đánh giá. Dữ liệu corrupted không được sửa trực tiếp để “che” lỗi. `papers_clean_repaired.json` bằng `papers_clean.json`; repaired answers giống hệt baseline answers, quality PASS và freshness FRESH. Đã chạy flow hai lần trên cùng snapshot và các kết quả chính không đổi; chưa kiểm thử tính idempotent trên một ngày chạy khác.

## 10. So sánh ba trạng thái

| Metric/signal | Baseline | Corrupted | Repaired | Corrupted − baseline | Repaired − corrupted |
| --- | ---: | ---: | ---: | ---: | ---: |
| `retrieval_hit_rate` | 1,0000 | 0,4000 | 1,0000 | −0,6000 | +0,6000 |
| `mean_token_f1` | 1,0000 | 0,6529 | 1,0000 | −0,3471 | +0,3471 |
| `judge_accuracy` (heuristic) | 1,0000 | 0,7000 | 1,0000 | −0,3000 | +0,3000 |
| `mean_judge_score` (heuristic) | 5,0000 | 3,4000 | 5,0000 | −1,6000 | +1,6000 |
| Quality gate | PASS | FAIL | PASS | — | Phục hồi |
| Freshness | FRESH | STALE | FRESH | — | Phục hồi |

Metrics trong ba file JSON khớp khi tính lại từ 30 answer records. Sau corruption, 6/10 câu miss DOI; 5 trong 6 DOI này nằm trong danh sách `drop_latest_records`, chứng minh mối liên hệ trực tiếp **bỏ bản ghi → không thể lấy lại DOI đó → hit rate giảm**. Câu miss thứ sáu không nằm trong danh sách bị xóa, nên chưa đủ bằng chứng để quy riêng cho lỗi title, summary hay index. Đồng thời duplicate và summary ngắn làm quality gate fail; ngày cũ làm freshness stale. Sau khi clean lại từ raw, 10/10 câu hit và các answer/metrics trở về đúng baseline. Đây là bằng chứng phục hồi cho **lần chạy hiện tại**, không chứng minh từng kịch bản riêng lẻ gây bao nhiêu điểm suy giảm.

## 11. Vấn đề tích hợp và độ tin cậy của bằng chứng

- **Môi trường:** Python mặc định trên máy rà soát thiếu `chromadb`; dùng `.venv` của dự án thì smoke test và cả hai flow đều chạy. Console Windows cần `PYTHONIOENCODING=utf-8` để in dòng tiếng Việt trong smoke test.
- **Freshness:** Bản đầu tiên đổi `published` nhưng giữ `age_days` cũ và chỉ làm cũ 4/23 dòng, chưa vượt SLA. Source đã được sửa để đồng bộ tuổi, kiểm tra tuổi theo cả hai trường và chọn tối thiểu 6 dòng; report mới ghi 7/23 stale, tức 30,43%, trạng thái STALE.
- **Câu hỏi authors:** Mẫu `Who are the authors...` ban đầu không khớp bộ tách đáp án trong `qa.py`. Source đã được sửa; baseline token F1 tăng từ 0,7000 ở lần chạy thử lên 1,0000 ở lần chạy chốt.
- **Lineage artifact:** Bộ JSON cũ không cùng schema và số dòng với source đã merge. Toàn bộ quality, metrics, answers, corruption log và report đã được sinh lại. Manifest embedding và phase 1 report hiện lưu đường dẫn tương đối để có thể dùng ở máy khác.

## 12. Giới hạn và bước hoàn thiện

| Giới hạn | Ảnh hưởng | Bước kiểm chứng tiếp theo |
| --- | --- | --- |
| Báo cáo cá nhân đã được cập nhật số liệu nhóm | Nội dung về phần việc và cam kết vẫn cần chủ sở hữu xác nhận | Mỗi thành viên tự rà lại báo cáo phần mình trước khi nộp |
| Judge dùng heuristic fallback; Ragas tắt | `judge_accuracy` không phải kết quả chấm bởi LLM; không có Ragas | Cấu hình judge thực, lưu model/run metadata; bật Ragas nếu bài nộp yêu cầu |
| Test set lấy từ 10 bài mới nhất và câu hỏi nêu nguyên tiêu đề | Lookup title có thể làm hit rate baseline lạc quan | Thêm câu hỏi diễn đạt lại không chứa title và đánh giá trên tập cố định độc lập |
| Sáu lỗi tiêm cùng lúc | Không định lượng được đóng góp của mỗi lỗi | Chạy ablation từng scenario với cùng test set và seed; so sánh metrics riêng |

## 13. Checklist trước khi nộp

- [x] Thông tin nhóm, vai trò và liên kết tới 5 báo cáo cá nhân đã đối chiếu với file hiện có.
- [x] Số liệu trong bảng khớp với metrics, answers, quality và freshness JSON vừa sinh lại.
- [x] Ba bộ answers dùng cùng 10 câu hỏi và ground-truth ID; repaired clean data bằng baseline.
- [x] `.venv/Scripts/python.exe -m pytest -q` đạt 4/4 test.
- [x] Baseline và corruption/repair flow chạy exit code 0 trên branch hiện tại.
- [x] Freshness phát hiện stale date và phục hồi sau repair.
- [x] Clean dataset, evaluation set, ba embedding manifests và Chroma index đã được tạo.
- [x] Rà soát và commit code, artifact, báo cáo mới trên branch hiện tại.
- [x] Tích hợp cập nhật mới của thành viên và push lên `main`.
- [ ] Các thành viên tự xác nhận nội dung báo cáo cá nhân đã cập nhật theo lần chạy mới.
- [ ] Kiểm tra contributor trên `main` và từng thành viên tự nộp link repository trên LMS.

Báo cáo này không chứa API key hay nội dung `.env`; các artifact mới đã được quét trước khi commit.

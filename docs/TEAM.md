# Danh Sách Thành Viên & Báo Cáo Phân Công Nhóm

- **Tên Nhóm:** `CDCV`
- **Mã Nhóm / Lớp:** `K4-L3-DAY10`
- **Tên Repository Nộp Bài:** `https://github.com/DngVinh/K4-L3A-Day10-Data-Pipeline-Data-Observability.git`
- **Email liên hệ nhóm:** `tendangc@gmail.com`

---

## # Thành viên

| STT | Họ và tên | MSSV | Email | Vai trò & Phân công công việc | Báo cáo cá nhân |
|---:|---|---|---|---|---|
| 1 | Đào Quang Cảnh | 2A202602542 | — | TV1 — Source owner (`src/ingestion/crossref.py`) | `report/daoquangcanh.md` |
| 2 | Trần Cao Thắng | 2A202602520 | — | TV2 — Cleaning & test-set owner (`src/ingestion/cleaning.py`, `src/evaluation/testset.py`) | `report/2A202602520_TranCaoThang.md` |
| 3 | Đặng Quốc Cường | 2A202602466 | — | TV3 — Observability owner (`src/observability/quality.py`, `src/observability/reporting.py`) | `report/dangquoccuong_report.md` |
| 4 | Nguyễn Anh Dũng | 2A202602554 | — | TV4 — Corruption & repair owner (`src/ingestion/corruption.py`; corrupted/repaired validation) | `report/2A202602554-NguyenAnhDung.md` |
| 5 | Dương Xuân Vinh | 2A202602622 | — | Trưởng nhóm / TV5 — Pipeline integration & evidence owner (`src/pipelines/phase1.py`, `src/pipelines/corruption_flow.py`; full-flow reproducibility) | `report/2A202602622_DuongXuanVinh.md` |

*Phân công trên bám theo bảng 5-member trong `report/README.md`; TV5 là đầu mối tích hợp, tái lập và tổng hợp bằng chứng toàn pipeline.*

---

## # Cá nhân

### ## Đào Quang Cảnh — TV1 — 2A202602542
- **Vai trò:** Source owner.
- **Phạm vi phụ trách / đầu ra:**
  - Thu thập và chuẩn hóa đầu vào Crossref trong `src/ingestion/crossref.py`.
  - Bảo đảm raw response, raw records và schema nguồn có thể truy vết, tái sử dụng.

### ## Trần Cao Thắng — TV2 — 2A202602520
- **Vai trò:** Cleaning & test-set owner.
- **Phạm vi phụ trách / đầu ra:**
  - Làm sạch, chuẩn hóa dữ liệu và tạo các trường phục vụ embedding trong `src/ingestion/cleaning.py`.
  - Xây dựng test set đánh giá trong `src/evaluation/testset.py`.
  - Bàn giao cleaned dataset và test set cho các bước downstream.

### ## Đặng Quốc Cường — TV3 — 2A202602466
- **Vai trò:** Observability owner.
- **Phạm vi phụ trách / đầu ra:**
  - Thiết lập quality checks, Great Expectations 1.x và freshness checks trong `src/observability/quality.py`.
  - Tạo các báo cáo chất lượng và báo cáo so sánh trong `src/observability/reporting.py`.
  - Theo dõi chất lượng baseline, corrupted và repaired.

### ## Nguyễn Anh Dũng — TV4 — 2A202602554
- **Vai trò:** Corruption & repair owner.
- **Phạm vi phụ trách / đầu ra:**
  - Triển khai các kịch bản corruption có kiểm soát trong `src/ingestion/corruption.py`.
  - Ghi corruption log, mô tả scenario và kiểm tra dữ liệu corrupted/repaired.
  - Phối hợp xác nhận khả năng repair từ raw snapshot.

### ## Dương Xuân Vinh — TV5 — 2A202602622
- **Vai trò:** Trưởng nhóm / Pipeline integration & evidence owner.
- **Phạm vi phụ trách / đầu ra:**
  - Điều phối luồng baseline trong `src/pipelines/phase1.py` và luồng corruption-repair trong `src/pipelines/corruption_flow.py`.
  - Bảo đảm toàn bộ pipeline chạy tái lập được, artifacts liên kết nhất quán và các chỉ số được tổng hợp.
  - Tổng hợp command, metrics, comparison report và bằng chứng nộp bài.

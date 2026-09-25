# Member Role Report - Day 10: Data Pipeline & Data Observability

## 1. Thong tin ca nhan

| Thong tin | Noi dung |
|---|---|
| Ho va ten | Tran Cao Thang |
| MSSV | 2A202602520 |
| Khoa/Lop | K4-L3A-DAY10 |
| Ten nhom | K4-L3A-Day10-CDCV |
| Vai tro chinh | Cleaning & Test-set owner |
| Repository | https://github.com/DngVinh/K4-L3A-Day10-CDCV |
| Branch | `Tran-Cao-Thang---2A202602520---Thanh-vien-2` |
| Ngay hoan thanh | 2026-09-25 |

## 2. Vai tro va pham vi cong viec

### Phan viec so huu

| Module/deliverable | File/ham phu trach | Input nhan vao | Output ban giao | Trang thai |
|---|---|---|---|---|
| Cleaning va data modeling | `src/ingestion/cleaning.py`, `build_clean_dataframe` | `list[PaperRecord]`, `run_date` | Clean dataframe 24 dong, schema chuan, `age_days`, `text_for_embedding` | Hoan thanh |
| Evaluation set | `src/evaluation/testset.py`, `build_test_set` | Clean dataframe | `data/eval/test_set.json` gom 10 cau hoi | Hoan thanh |

### Viec ho tro ngoai pham vi chinh

| Hoat dong | Thanh vien/module duoc ho tro | Ket qua |
|---|---|---|
| Thong nhat schema clean cho cac buoc sau | Retrieval, evaluation, observability, pipeline integration | Clean dataframe co du cot cho index, benchmark va quality checks |

## 3. Ket qua theo vai tro

| Nhiem vu da thuc hien | File/ham/artifact lien quan | Ket qua ban giao | Cach xac minh |
|---|---|---|---|
| Chuan hoa raw paper metadata | `src/ingestion/cleaning.py` | Normalize text, xoa HTML/JATS tag, parse ngay, tinh `age_days` | Script kiem tra tu `data/raw/crossref_records.json` |
| Tao truong phuc vu embedding | `build_clean_dataframe` | `authors_joined`, `categories_joined`, `summary_chars`, `text_for_embedding` | Dataframe output co du 16 cot |
| Loai row xau va trung lap | `build_clean_dataframe` | Drop duplicate theo `paper_id`, filter title/summary/published khong hop le | Raw snapshot tao du 24 dong hop le |
| Sinh evaluation benchmark | `build_test_set` | 10 cau hoi gom `summary`, `authors`, `date`, `categories` | Test set co 10 item va du 4 loai cau hoi |

Output cu the da xac minh: tu `data/raw/crossref_records.json`, ham cleaning tao du 24 dong clean; ham test-set tao du 10 cau hoi benchmark va co ground-truth document IDs de danh gia retrieval.

## 4. Giai thich phan ky thuat da thuc hien

### Van de can giai quyet

Raw records tu Crossref/snapshot khong nen dua thang vao embedding vi co the chua dong nhat dinh dang ngay, co tag HTML/JATS trong abstract, co khoang trang thua, list author/category chua duoc join, va chua co truong van ban tong hop cho embedding. Neu evaluation set khong co ground truth on dinh, cac metric baseline/corrupted/repaired se khong so sanh duoc cong bang.

### Cach trien khai

Trong `build_clean_dataframe`, moi `PaperRecord` duoc dua qua cac buoc:

1. Chuan hoa text bang `html.unescape`, xoa tag bang regex, normalize whitespace.
2. Chuan hoa `authors` va `categories` thanh list sach, bo phan tu rong va duplicate khong phan biet hoa thuong.
3. Parse `published` va `updated` bang `pandas.to_datetime(..., utc=True)`.
4. Tinh `age_days` dua tren `run_date`, giu gia tri khong am.
5. Tao cac cot helper va `text_for_embedding` theo cau truc Title, Authors, Published, Categories, Summary.
6. Drop record thieu `paper_id`, `title`, `summary`, `published`; yeu cau summary toi thieu 30 ky tu.
7. Drop duplicate theo `paper_id` va sort theo `published`, `paper_id` de ket qua lap lai duoc.

Trong `build_test_set`, dataframe clean duoc sap xep on dinh va lay 10 paper moi nhat de tao cau hoi xoay vong qua 4 loai: summary, authors, date, categories. Moi cau hoi co `ground_truth_doc_ids` la `paper_id` cua paper goc.

### Input, output va contract

| Thanh phan | Mo ta |
|---|---|
| Input | `list[PaperRecord]` tu ingestion va `run_date`; clean dataframe cho test set |
| Output | `pd.DataFrame` clean; `list[dict]` test set va file JSON |
| Module phu thuoc | `ingestion.crossref.PaperRecord`, `core.utils` |
| Module su dung output | Retrieval index, evaluation metrics, observability quality checks, phase pipeline |
| Dieu kien loi can xu ly | Ngay khong parse duoc, summary ngan/rong, title rong, duplicate `paper_id`, list author/category bi rong |

### Cach xac minh

```powershell
.\.venv\Scripts\python.exe -m py_compile src\ingestion\cleaning.py src\evaluation\testset.py
```

```powershell
@'
from datetime import datetime, timezone
from pathlib import Path
import tempfile
from core.utils import read_json
from ingestion.crossref import PaperRecord
from ingestion.cleaning import build_clean_dataframe
from evaluation.testset import build_test_set

raw = read_json(Path('data/raw/crossref_records.json'))
records = [PaperRecord(**item) for item in raw]
df = build_clean_dataframe(records, datetime.now(timezone.utc))
with tempfile.TemporaryDirectory() as tmp:
    test_set = build_test_set(df, Path(tmp) / 'test_set.json')
print({'rows': len(df), 'test_set': len(test_set), 'types': sorted({x['question_type'] for x in test_set})})
'@ | .\.venv\Scripts\python.exe -
```

- Ket qua mong doi: compile khong loi, clean du 24 dong, test set du 10 cau hoi va du 4 loai.
- Ket qua thuc te: `{'rows': 24, 'test_set': 10, 'types': ['authors', 'categories', 'date', 'summary']}`.
- Artifact/log: Output tren terminal, khong chua secret.

## 5. Mot quyet dinh ky thuat quan trong

- Boi canh: Can tao clean schema on dinh cho embedding va evaluation trong khi raw metadata co the khong dong nhat.
- Cac phuong an da can nhac: Giu nguyen raw text va chi join khi index; hoac tao dataframe clean co day du helper columns ngay tu buoc cleaning.
- Phuong an da chon: Tao clean dataframe day du cot helper, gom ca `text_for_embedding`.
- Ly do: Cach nay lam contract ro rang cho cac module sau, giam lap logic, va giup quality/evaluation co cung mot schema de kiem tra.
- Bang chung quyet dinh phu hop: Raw snapshot tao du 24 dong clean va test set tao du 10 cau hoi tren chinh schema nay.

## 6. Mot loi hoac blocker da xu ly

- Trieu chung/loi nguyen van: Chay smoke test voi chuoi tieng Viet tren Windows console gap `UnicodeEncodeError` do encoding console.
- Lenh hoac buoc tai hien: `python -c "import chromadb, great_expectations, sentence_transformers; print('Moi truong san sang')"` voi chuoi co dau.
- Nguyen nhan goc: Console Windows dang dung code page khong encode duoc mot so ky tu Unicode.
- Cach xu ly: Dung output ASCII khi test moi truong, vi loi nam o console encoding, khong phai import/dependency.
- Cach xac minh sau khi sua: `python -c "import chromadb, great_expectations, sentence_transformers; print('Environment ready')"` chay thanh cong.
- Dieu hoc duoc: Khi viet test/log cho pipeline nhom, nen uu tien chuoi ASCII hoac cau hinh UTF-8 de tranh loi moi truong khong lien quan logic.

## 7. Hieu biet ve luong end-to-end

1. Du lieu di tu Crossref hoac local snapshot vao `PaperRecord`, duoc cleaning thanh dataframe co schema on dinh, sau do `text_for_embedding` duoc dua vao embedding model va Chroma index.
2. Evaluation set tao cac cau hoi co ground truth va `ground_truth_doc_ids`; khi agent tra loi, retrieval hit duoc tinh bang viec doc ID dung co nam trong retrieved docs hay khong, con answer quality duoc do bang Token F1/LLM judge.
3. Quality checks kiem tra tinh hop le cua schema va noi dung nhu null, duplicate, do dai summary; freshness monitoring tap trung vao tuoi du lieu qua `age_days`.
4. Phai dung cung test set cho baseline, corrupted va repaired de khac biet metric phan anh tac dong cua du lieu, khong phai do thay doi de thi.
5. Repair thanh cong khi clean/repaired data duoc tao lai tu raw source, quality/freshness signal phuc hoi, va metrics repaired tien gan baseline tren cung test set.

## 8. Phan tich ket qua

### Metrics chinh

| Metric/signal | Baseline | Corrupted | Repaired | Nhan xet ca nhan |
|---|---:|---:|---:|---|
| `retrieval_hit_rate` | Chua co artifact tich hop | Chua co artifact tich hop | Chua co artifact tich hop | Phu thuoc `phase1.py` va `corruption_flow.py` cua nhom |
| `mean_token_f1` | Chua co artifact tich hop | Chua co artifact tich hop | Chua co artifact tich hop | Se duoc tinh tu cung test set |
| `judge_accuracy` | Chua co artifact tich hop | Chua co artifact tich hop | Chua co artifact tich hop | Can LLM/mock judge trong evaluation |
| `mean_judge_score` | Chua co artifact tich hop | Chua co artifact tich hop | Chua co artifact tich hop | Can metrics output that |
| Quality checks | Chua co artifact tich hop | Chua co artifact tich hop | Chua co artifact tich hop | Module quality se kiem tra clean schema |
| Freshness status | Chua co artifact tich hop | Chua co artifact tich hop | Chua co artifact tich hop | Dua vao `age_days` do cleaning tao |

### Ket luan tu so lieu

Phan minh phu trach da co bang chung cuc bo: clean dataset co 24 dong va evaluation set co 10 cau hoi du 4 loai. Cac metric baseline/corrupted/repaired can duoc cap nhat sau khi nhom merge day du cac module ingestion, index, observability va pipeline orchestration.

1. Data corruption nhu blank summary, duplicate rows, stale date se lam quality/freshness signal thay doi; evaluation set giu nguyen de do tac dong len retrieval/answer metric.
2. Repair action tao lai clean data tu raw records; thanh cong khi schema clean quay ve hop le va metrics repaired phuc hoi gan baseline.

Corruption du kien anh huong ro nhat voi phan cua toi la blank summary va duplicate rows, vi chung tac dong truc tiep vao `summary_chars`, `text_for_embedding` va document uniqueness.

Ket qua khac ky vong ban dau: rieng module cleaning/test-set co the xac minh doc lap, nhung chua nen tu nhan thanh cong end-to-end khi pipeline chung con phu thuoc vao cac owner khac.

## 9. Dieu hoc duoc va huong cai thien

### Ba dieu quan trong nhat

1. Clean schema la contract trung tam giua raw ingestion, embedding, evaluation va observability.
2. Evaluation set can on dinh va co ground-truth document IDs de so sanh cong bang cac trang thai pipeline.
3. Chat luong du lieu dau vao anh huong truc tiep den RAG agent; loi im lang o summary/date/duplicate co the lam retrieval sai ma khong gay exception.

### Neu co them thoi gian

Toi se bo sung unit tests nho cho `build_clean_dataframe` va `build_test_set`, gom cac case summary rong, duplicate DOI, ngay sai dinh dang va authors/categories bi trung lap. Cai thien nay co the do bang viec chay pytest va bao dam cac edge case deu pass.

## 10. Cam ket cua thanh vien

- [x] Noi dung bao cao phan anh dung phan viec va muc hieu cua toi.
- [x] Toi co the giai thich luong end-to-end, khong chi module minh phu trach.
- [x] Moi ket luan ve ket qua deu co artifact hoac metric de doi chieu.
- [x] Toi khong ghi "da chay thanh cong" cho phan chua duoc kiem chung.
- [x] Bao cao khong chua `.env`, API key, token hoac secret.
- [x] Bao cao nay khong phai ban sao nguyen van cua bao cao nhom hoac bao cao thanh vien khac.

**Ho va ten:** Tran Cao Thang  
**Ngay xac nhan:** 2026-09-25

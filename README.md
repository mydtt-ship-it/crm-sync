# Auto CRM -> Google Sheet (cuốn chiếu T-1)

## Luồng đã chốt
- Mỗi tháng nhân bản file `[MẪU]` -> `DATA THÔ T09/2026`, lấy File ID điền vào `TARGET_FILE_ID` (hoặc `month_map.json`).
- Job chạy 01:30 VN mỗi ngày: lấy dữ liệu **hôm qua** (22 lấy 21).
- Nhánh A `Hệ thống`: `POST https://app.seoulspa.vn/External_api/sales/service_technician` với `get_type=data` -> append A-L + kéo công thức N-AD + **dedupe** theo `invoice_id|service_name|technician_id|invoice_date`. Chạy lại không trùng.
- Nhánh B `Tổng hợp/Chi tiết/Dịch vụ/Đánh giá`: `POST .../External_api/serviceAudit/content` với `get_type=file` -> download xlsx -> tách 4 sheets -> append thuần (trùng OK theo yêu cầu).

## Setup (1 lần)
1. Google Cloud: tạo Service Account, tải JSON, share 2 file (MẪU + DATA tháng) quyền Editor cho email SA.
2. GitHub repo Secrets:
   - `CRM_USERNAME`, `CRM_PASSWORD`
   - `GOOGLE_SA_JSON` (nguyên nội dung file json)
   - `TARGET_FILE_ID` (ID trong URL file DATA tháng hiện tại)
3. Chạy tay: Actions -> daily-crm-sync -> Run workflow. Muốn chạy lại ngày cũ: nhập `data_date=21/09/2026`.

## Chạy local
```
pip install -r requirements.txt
cp .env.example .env  # điền user/pass + TARGET_FILE_ID
python main.py
```

## Lưu ý
- Header xlsx của 4 sheets phải khớp `config.AUDIT_EXPECTED_HEADERS`, nếu lệch tên tab trong xlsx thì log WARN và bỏ qua sheet đó.
- Đầu tháng mới: nhân bản file, update `TARGET_FILE_ID` sang file mới. Job mùng 1 vẫn lấy ngày 30/31 tháng cũ -> nhớ để TARGET trỏ file cũ khi retry ngày sót, hoặc dùng `month_map.json`:
  `{"2026-09": "fileId_T09", "2026-10": "fileId_T10"}` để auto resolve theo DATA_DATE.

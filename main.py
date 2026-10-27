"""Job daily T-1: hôm nay 22 -> lấy 21. Re-run an toàn cho Hệ thống (dedupe), 4 sheets kia append thuần."""
import json
import os
import tempfile
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
from dotenv import load_dotenv

import config
import crm_client
import sheets_helper

VN = ZoneInfo("Asia/Ho_Chi_Minh")


def resolve_data_date() -> str:
    manual = os.getenv("DATA_DATE", "").strip()  # dd/mm/yyyy
    if manual:
        return manual
    yesterday = datetime.now(VN).date() - timedelta(days=1)
    return yesterday.strftime("%d/%m/%Y")


def resolve_target_file() -> str:
    # V1: 1 file/tháng do bạn nhân bản manual, truyền qua env.
    # V2: dùng month_map.json {"2026-09": fileId}. Nếu có file này thì tự resolve theo DATA_DATE.
    fid = os.getenv("TARGET_FILE_ID", "").strip()
    data_date = resolve_data_date()
    if os.path.exists("month_map.json"):
        with open("month_map.json", encoding="utf-8") as f:
            m = json.load(f)
        key = datetime.strptime(data_date, "%d/%m/%Y").strftime("%Y-%m")
        if key in m:
            return m[key]
    if not fid:
        raise RuntimeError("Thiếu TARGET_FILE_ID (hoặc month_map.json chưa có tháng này). Nhân bản file MẪU rồi điền ID vào.")
    return fid


def main() -> None:
    load_dotenv()
    user = os.environ["CRM_USERNAME"]
    pwd = os.environ["CRM_PASSWORD"]
    base = os.getenv("CRM_BASE_URL", config.CRM_BASE_URL)
    sa_path = os.getenv("GOOGLE_SA_JSON", "sa.json")

    data_date = resolve_data_date()
    file_id = resolve_target_file()
    print(f"[sync] date={data_date} file={file_id}")

    gc = sheets_helper.get_client(sa_path)
    sh = gc.open_by_key(file_id)

    # --- Nhánh A: Hệ thống (dedupe, không trùng) ---
    raw_ht = crm_client.fetch_he_thong(data_date, user, pwd, base)
    print(f"[he-thong] api rows={len(raw_ht)}")
    existing_keys = sheets_helper.read_he_thong_keys(sh, config.SHEET_HE_THONG)
    to_add, seen = [], set()
    for r in raw_ht:
        k = config.he_thong_key(r)
        if k in existing_keys or k in seen:
            continue
        seen.add(k)
        to_add.append([r.get(c, "") for c in config.HE_THONG_COLUMNS])
    n_ht = sheets_helper.append_rows_and_fill_formula(sh, config.SHEET_HE_THONG, to_add)
    print(f"[he-thong] appended={n_ht} skipped_dup={len(raw_ht) - len(to_add)}")

    # --- Nhánh B: 4 sheets audit (append thuần, trùng OK) ---
    file_url = crm_client.fetch_audit_file_url(data_date, user, pwd, base)
    print(f"[audit] xlsx url={file_url}")
    tmp = os.path.join(tempfile.gettempdir(), f"audit_{data_date.replace('/', '-')}.xlsx")
    crm_client.download_file(file_url, tmp)
    xls = pd.ExcelFile(tmp, engine="openpyxl")
    summary = {}
    for title in config.SHEETS_AUDIT:
        if title not in xls.sheet_names:
            print(f"[audit:{title}] WARN không thấy trong xlsx ({xls.sheet_names}), bỏ qua")
            continue
        df = pd.read_excel(xls, sheet_name=title, dtype=str).fillna("")
        # Bỏ dòng header trùng nếu file có header lặp + bỏ dòng trống hoàn toàn
        rows = df.values.tolist()
        rows = [r for r in rows if any(str(x).strip() != "" for x in r)]
        n = sheets_helper.append_rows_and_fill_formula(sh, title, rows)
        summary[title] = n
        print(f"[audit:{title}] appended={n}")
    print(f"[done] date={data_date} he_thong={n_ht} audit={summary}")


if __name__ == "__main__":
    main()

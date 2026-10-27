"""Ghi Google Sheet: append raw + kéo công thức + dedupe Hệ thống."""
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.readonly"]


def get_client(sa_json_path: str) -> gspread.Client:
    creds = Credentials.from_service_account_file(sa_json_path, scopes=SCOPES)
    return gspread.authorize(creds)


def get_oauth_client(token_path: str = "token.json") -> gspread.Client:
    """Client OAuth theo Gmail ca nhan (thay the SA khi bi chan tao key)."""
    from google.oauth2.credentials import Credentials as UserCreds
    creds = UserCreds.from_authorized_user_file(token_path, scopes=SCOPES)
    return gspread.authorize(creds)


def get_sheet_id(sh: gspread.Spreadsheet, title: str) -> int:
    ws = sh.worksheet(title)
    return ws.id


def read_he_thong_keys(sh: gspread.Spreadsheet, title: str) -> set[str]:
    """Đọc key chống trùng Hệ thống từ data hiện có. Key = invoice|service|tech|date."""
    ws = sh.worksheet(title)
    # A-L: customer_id(A), invoice_id(D), invoice_date(E), service_name(H), technician_id(J)
    vals = ws.get("A2:L", value_render_option="UNFORMATTED_VALUE")
    keys = set()
    for r in vals:
        r = (r + [""] * 12)[:12]
        keys.add(f"{r[3]}|{r[7]}|{r[9]}|{r[4]}")
    return keys


def append_rows_and_fill_formula(sh: gspread.Spreadsheet, title: str, rows: list[list]) -> int:
    """Append raw rows, sau đó copy công thức từ dòng trên xuống (PASTE_FORMULA tự nhảy ref)."""
    if not rows:
        return 0
    ws = sh.worksheet(title)
    # Dòng cuối hiện tại (tính cả header). Nếu sheet trống ngoài header thì start=2.
    existing = ws.get_all_values()
    start_row = len(existing) + 1 if existing else 2
    ncols = max(len(r) for r in rows)
    # 1. Append values
    ws.append_rows(rows, value_input_option="USER_ENTERED", insert_data_option="INSERT_ROWS")

    # 2. Tìm cột công thức ở dòng mẫu (dòng ngay trước vùng mới append).
    # Đọc dòng mẫu với FORMULA để biết ô nào là công thức.
    if start_row <= 2:
        return len(rows)  # chưa có dòng mẫu để copy
    formulas = ws.get(f"{start_row - 1}:{start_row - 1}", value_render_option="FORMULA")
    if not formulas or not formulas[0]:
        return len(rows)
    template = formulas[0]
    formula_cols = [i for i, v in enumerate(template) if isinstance(v, str) and v.startswith("=")]
    # Chỉ copy các cột nằm sau vùng raw (tránh đè raw)
    formula_cols = [i for i in formula_cols if i >= ncols]
    if not formula_cols:
        return len(rows)

    first, last = min(formula_cols), max(formula_cols)
    src = {"sheetId": ws.id, "startRowIndex": start_row - 2, "endRowIndex": start_row - 1,
           "startColumnIndex": first, "endColumnIndex": last + 1}
    dst = {"sheetId": ws.id, "startRowIndex": start_row - 1, "endRowIndex": start_row - 1 + len(rows),
           "startColumnIndex": first, "endColumnIndex": last + 1}
    sh.batch_update({"requests": [{
        "copyPaste": {"source": src, "destination": dst, "pasteType": "PASTE_FORMULA", "pasteOrientation": "NORMAL"}
    }]})
    return len(rows)


# --- Video Queue 0d (them moi). Chay doc lap, khong anh huong sheet cu. ---
def ensure_video_queue(sh, title: str, headers: list[str]) -> None:
    """Tao tab Video_Queue + header neu chua co. Chay 1 lan."""
    try:
        ws = sh.worksheet(title)
    except Exception:
        ws = sh.add_worksheet(title=title, rows=200, cols=len(headers))
        ws.update("A1", [headers])
        return
    vals = ws.get("A1:Z1")
    if not vals or not any(vals[0]):
        ws.update("A1", [headers])


def queue_add(sh, title: str, row: list) -> int:
    """Them 1 video todo. row = [san_pham, hook, voice_script, on_screen, status, video_file]."""
    ws = sh.worksheet(title)
    ws.append_row(row, value_input_option="USER_ENTERED")
    return 1


def queue_get_todo(sh, title: str) -> list[dict]:
    """Doc cac dong status=todo. Tra ve list dict kem _row_index (de update sau)."""
    ws = sh.worksheet(title)
    records = ws.get_all_records()
    todos = []
    for i, r in enumerate(records, start=2):
        if str(r.get("status", "")).strip().lower() in ("todo", "moi", ""):
            r["_row_index"] = i
            todos.append(r)
    return todos


def queue_mark_done(sh, title: str, row_index: int, video_file: str) -> None:
    """Danh dau done + dien ten file video. status o cot E, video_file o cot F."""
    ws = sh.worksheet(title)
    ws.update_cell(row_index, 5, "done")
    ws.update_cell(row_index, 6, video_file)

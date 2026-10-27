"""Gọi CRM API. Endpoint + base URL theo bạn cung cấp."""
import requests
import config

TIMEOUT = 120


def _post(path: str, payload: dict, base_url: str) -> dict:
    url = base_url.rstrip("/") + path
    r = requests.post(url, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    body = r.json()
    if body.get("status") != 200:
        raise RuntimeError(f"CRM lỗi: {body.get('status')} - {body.get('message')}")
    return body


def fetch_he_thong(date_ddmmyyyy: str, username: str, password: str, base_url: str = config.CRM_BASE_URL) -> list[dict]:
    """Sheet Hệ thống: luôn dùng get_type=data để có JSON append + dedupe."""
    body = _post(config.ENDPOINT_HE_THONG, {
        "username": username,
        "password": password,
        "start_date": date_ddmmyyyy,
        "end_date": date_ddmmyyyy,
        "store_ids": [],
        "get_type": "data",
    }, base_url)
    data = body.get("data") or []
    return data if isinstance(data, list) else []


def fetch_audit_file_url(date_ddmmyyyy: str, username: str, password: str, base_url: str = config.CRM_BASE_URL) -> str:
    """4 sheets còn lại: dùng get_type=file, trả về link xlsx chứa 4 sheets."""
    body = _post(config.ENDPOINT_AUDIT, {
        "username": username,
        "password": password,
        "start_date": date_ddmmyyyy,
        "end_date": date_ddmmyyyy,
        "store_ids": [],
        "get_type": "file",
    }, base_url)
    url = body.get("data")
    if not url or not isinstance(url, str):
        raise RuntimeError(f"API audit không trả về link file: {body}")
    return url


def download_file(url: str, dest: str) -> str:
    with requests.get(url, stream=True, timeout=TIMEOUT) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                if chunk:
                    f.write(chunk)
    return dest

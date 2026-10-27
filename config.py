"""Cấu hình trung tâm. Không chứa mật khẩu, chỉ chứa mapping."""
CRM_BASE_URL = "https://app.seoulspa.vn"
ENDPOINT_HE_THONG = "/External_api/sales/service_technician"
ENDPOINT_AUDIT = "/External_api/serviceAudit/content"

# Tên sheet đích trong file DATA THÔ THÁNG (phải khớp 100% tên tab)
SHEET_HE_THONG = "Hệ thống"
SHEETS_AUDIT = ["Tổng hợp", "Chi tiết", "Dịch vụ", "Đánh giá"]

# Thứ tự cột raw sheet Hệ thống (A-L) map từ description API
HE_THONG_COLUMNS = [
    "customer_id", "customer_name", "customer_phone", "invoice_id",
    "invoice_date", "store_name", "category_name", "service_name",
    "technician_name", "technician_id", "usage_status", "management_region",
]

# Header raw kỳ vọng của 4 sheets (để validate file xlsx tải về)
AUDIT_EXPECTED_HEADERS = {
    "Tổng hợp": ["ID lịch hẹn", "ID khách hàng", "Tên khách hàng", "Chi nhánh", "Ngày tạo", "Mã yêu cầu", "Xử lý lại từ yêu cầu", "Loại phiếu", "Ghi chú", "Trạng thái", "Lý do hủy", "Thời gian bắt đấu", "Thời gian kết thúc", "Số lần duyệt phác thảo", "Số lần duyệt Kết quả", "Khu vực quản lý", "Người báo cáo", "Người thực hiện dịch vụ", "Ngày hẹn (khách đến)"],
    "Chi tiết": ["Mã yêu cầu", "Người thực hiện", "ID người thực hiện", "Hành động", "Ghi chú", "Thời gian tạo", "Thời gian xử lý(giây)"],
    "Dịch vụ": ["Mã yêu cầu", "Mã dịch vụ", "Dịch vụ", "Mã nhóm", "Tên nhóm"],
    "Đánh giá": ["ID yêu cầu", "Loại", "Chi tiết", "Người đánh giá", "Thời gian đánh giá", "Người cập nhật", "Thời gian cập nhật"],
}


def he_thong_key(row: dict) -> str:
    """Key chống trùng sheet Hệ thống. Re-run cùng ngày không tạo trùng."""
    return f"{row.get('invoice_id')}|{row.get('service_name')}|{row.get('technician_id')}|{row.get('invoice_date')}"

# --- Video AI TikTok 0d (them moi, chua can Sheet that van chay local) ---
SHEET_VIDEO_QUEUE = "Video_Queue"
VIDEO_QUEUE_COLUMNS = [
    "san_pham", "hook", "voice_script", "on_screen", "status", "video_file",
]

# Bài Lab 27: Đánh giá Churn Risk với Human-in-the-Loop

Đây là bài làm cho Lab 27: Xây dựng workflow LangGraph đánh giá khách hàng với Human-in-the-Loop.

## 1. Cách cài đặt dependency
Dự án sử dụng Python 3.10+. Khuyến nghị sử dụng `uv` để quản lý môi trường:
```bash
uv venv
.venv\Scripts\activate  # (Trên Windows)
# hoặc source .venv/bin/activate (Trên macOS/Linux)

uv pip install -r requirements.txt
```
Lưu ý: Bạn cần tạo một file `.env` chứa API Key thật của OpenRouter trước khi chạy (Tham khảo template trong `.env.example` hoặc trong `.env`).
```env
OPENROUTER_API_KEY=your_key_here
OPENAI_BASE_URL=https://openrouter.ai/api/v1
```

## 2. Cách chạy LangGraph Workflow và Streamlit UI
Workflow đã được tích hợp chặt chẽ với Streamlit UI. Để chạy toàn bộ hệ thống:
```bash
streamlit run app.py
```
Sau đó truy cập vào trình duyệt tại `http://localhost:8501`.

## 3. Các chính sách điều hướng (Routing & Policy Rules)

### Confidence Threshold
Ngưỡng điểm tin cậy (Confidence Threshold) đang sử dụng là **0.85**. 
- Nếu Agent trả về điểm tin cậy `< 0.85`, hành động đó sẽ bị đưa vào luồng kiểm duyệt (Escalate to Human).

### Hard Policy Rule
- Bất kể điểm tin cậy là bao nhiêu, mọi đề xuất có hành động (Action) là `increase_credit_limit` đều **bắt buộc phải qua kiểm duyệt của con người**.

## 4. Cách Approve, Reject và Edit trên Streamlit
Khi một hành động bị tạm dừng (Interrupted) và chờ duyệt, giao diện Streamlit sẽ hiển thị phần **Pending Actions (Human Review)**:
- **Approve (✅):** Đồng ý với đề xuất của Agent. Hành động sẽ được thông qua.
- **Reject (❌):** Từ chối đề xuất. Hành động sẽ bị hủy bỏ (abort).
- **Edit & Approve (✏️):** Bạn có thể gõ một hành động mới vào ô "Edit Action" và nhấn Edit & Approve. Hành động mới này sẽ được ghi đè và hệ thống sẽ thực thi hành động đã sửa.

Mỗi khi bạn nhấn một trong các nút này, đồ thị LangGraph sẽ được nạp lại state và gọi `.invoke()` để tiếp tục luồng thực thi.

## 5. Lưu trữ Audit Log
Mọi quyết định sau quá trình Human Review đều được lưu tự động theo cấu trúc `AuditEntry` vào file cục bộ:
- **File:** `audit_log.json`
- Định dạng: Mảng JSON, được append liên tục mỗi khi có quyết định mới.

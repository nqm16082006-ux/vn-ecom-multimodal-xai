# VN E-Commerce Multimodal XAI

> **Đề tài KH&CN Sinh viên năm 2027**
> *Nghiên cứu phát triển mô hình học sâu đa phương thức kết hợp trí tuệ nhân tạo giải thích (XAI) trong phát hiện gian lận mô tả sản phẩm và đánh giá ảo trên sàn thương mại điện tử tiếng Việt*

- **Tác giả**: Ngô Quang Minh (`KHMT K23A`, Khoa CNTT)
- **GV Hướng dẫn**: TS. Trần Quang Quý

## Mục tiêu chính
1. Xây dựng bộ dữ liệu đa phương thức tiếng Việt từ sàn thương mại điện tử (Shopee, TikTok Shop) gồm văn bản mô tả, ảnh quảng cáo, bình luận, ảnh chụp thực tế và đặc trưng hành vi.
2. Phát triển mô hình học sâu đa phương thức kết hợp **PhoBERT**, **ViT/CLIP** và **Cross-Attention Fusion** để phát hiện đánh giá ảo và sai lệch mô tả sản phẩm.
3. Tích hợp **Explainable AI (XAI)**: `SHAP` cho văn bản & đặc trưng hành vi, `Grad-CAM` / Attention Heatmap cho vùng ảnh bất thường.
4. Xây dựng ứng dụng Web Demo gồm **Backend** (Python/FastAPI) và **Frontend** (React).

## Cấu trúc dự án (dự kiến)
- `backend/`: API suy luận mô hình, tính điểm tin cậy và xuất giải thích XAI (FastAPI).
- `frontend/`: Giao diện Web Demo trực quan (React).
- `configs/`: Tệp cấu hình tham số và đường dẫn.
- `scripts/`: Các công cụ tiện ích hỗ trợ dự án.

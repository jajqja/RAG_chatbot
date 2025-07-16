# RAG_chatbot

Đây là một dự án nhỏ được phát triển trong quá trình thực tập tại một công ty AI, với mục tiêu xây dựng một chatbot thông minh có khả năng trả lời câu hỏi dựa trên tài liệu do người dùng cung cấp, ứng dụng kỹ thuật RAG (Retrieval-Augmented Generation).


## Mục tiêu

Phát triển một chatbot có khả năng:
  - Hiểu câu hỏi của người dùng.
  - Truy xuất thông tin từ các tài liệu đã được tải lên hệ thống.
  - Tạo câu trả lời tự nhiên, chính xác nhờ vào sự kết hợp giữa LLM và vector database.

Ngoài việc truy vấn tài liệu, chatbot còn tích hợp các công cụ như:
  - Tóm tắt nội dung
  - Dịch văn bản
  - Tìm kiếm trên web
Những công cụ này được mô hình xem như các tools, giúp mở rộng phạm vi và chất lượng của câu trả lời.

## Kiến trúc & Hướng tiếp cận
Khi một tài liệu được người dùng tải lên, hệ thống sẽ thực hiện các bước sau:
  - Chia nhỏ tài liệu thành các đoạn (chunk).
  - Sinh embedding cho mỗi đoạn và lưu vào vector database (Qdrant).
  - Tóm tắt nội dung của từng đoạn nhỏ, sau đó ghép lại để tạo thành một bản tóm tắt tổng quan.
  - Lưu trữ tóm tắt vào file .json, nhằm đảm bảo dữ liệu không bị mất khi hệ thống khởi động lại.
  - Tạo một tool tương ứng với mỗi tài liệu, trong đó phần mô tả (description) chính là bản tóm tắt. Điều này giúp LLM lựa chọn đúng tài liệu khi cần thực hiện RAG.

Khi người dùng đặt câu hỏi, hệ thống sẽ:
  - Phân tích mục đích của câu hỏi.
  - Tự động lựa chọn công cụ phù hợp (RAG từ tài liệu nào, dịch, tóm tắt, hay tìm kiếm web).
  - Tạo ra câu trả lời cuối cùng dựa trên kết quả thu thập được từ các công cụ này.

## Điểm mạnh của hệ thống
- Khả năng duy trì dữ liệu lâu dài: Các tài liệu và tóm tắt được lưu trữ dưới dạng vector (trong Qdrant) và file .json, đảm bảo không mất dữ liệu khi hệ thống khởi động lại.
- Linh hoạt mở rộng: Mỗi tài liệu được định nghĩa như một "tool", giúp hệ thống linh hoạt và dễ mở rộng.
- Tối ưu trải nghiệm người dùng: Kết hợp nhiều công cụ thông minh giúp chatbot trả lời tốt hơn trong nhiều ngữ cảnh.

## Cách triển khai

Trước khi chạy cần:

```bash
export OPENAI_API_KEY="sk-..."
export TAVILY_API_KEY="tvly-..."
export QDRANT_URL = "https..."
export QDRANT_API_KEY = "eyJh..."
```

Chạy giao diện:

```bash
streamlit run app.py
```

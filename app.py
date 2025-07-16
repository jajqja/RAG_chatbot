import streamlit as st
from chatbot import Chatbot
import os

# Cấu hình giao diện
# Version 4.0: Dùng key xịn
st.set_page_config(page_title="Chatbot version 4.0")

st.title("Demo Simple RAG Chatbot")

# Khởi tạo chatbot 1 lần
@st.cache_resource
def load_chatbot():
    return Chatbot()

chatbot = load_chatbot()

# Tính năng tải lên tài liệu
uploaded_file = st.file_uploader("Tải lên tài liệu văn bản", type=["txt","pdf","docx"], accept_multiple_files=True)

if uploaded_file:
    if st.button("Áp dụng"):
        docs_folder = "data/docs"
        files_exist = any(os.scandir("data"))

        for file in uploaded_file:
            file_path = os.path.join(docs_folder, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            chatbot.build_tool_and_index(file_path)

        st.success("Đã thêm tài liệu mới. Bạn có thể bắt đầu trò chuyện!")


# Lưu hội thoại
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị các tin nhắn trước đó
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Người dùng gửi tin nhắn
user_input = st.chat_input("Nhập câu hỏi của bạn...")
if user_input:
    # Hiển thị câu hỏi
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Lấy câu trả lời từ chatbot
    with st.chat_message("assistant"):
        with st.spinner("Đang xử lý..."):
            answer = chatbot.ask(user_input)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})


# tools.py
from deep_translator import GoogleTranslator
from langchain.tools import tool
from langchain_core.language_models import BaseLanguageModel
from tavily import TavilyClient
import os

def get_summarize_tool(llm: BaseLanguageModel):
    @tool
    def summarize_text(text: str) -> str:
        """Tóm tắt nội dung đầu vào bằng tiếng Việt sử dụng mô hình ngôn ngữ."""
        prompt = f"Hãy tóm tắt đoạn văn sau bằng tiếng Việt:\n\n{text}"
        return llm.invoke(prompt)
    
    return summarize_text

@tool
def translate_text(text: str, target_lang: str = "vi") -> str:
    """Dịch nội dung đầu vào sang ngôn ngữ mong muốn (ví dụ: 'vi', 'en', 'fr')."""
    translator = GoogleTranslator(source='auto', target=target_lang)
    return translator.translate(text)

@tool
def search_web(query: str) -> str:
    """Tra cứu thông tin mới nhất từ internet về một chủ đề bất kỳ và trả lời bằng tiếng việt"""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Lỗi: TAVILY_API_KEY chưa được cấu hình."

    tavily = TavilyClient(api_key=api_key)
    results = tavily.search(query=query, search_depth="advanced")
    snippets = [r["content"] for r in results["results"]]
    return "\n\n".join(snippets)
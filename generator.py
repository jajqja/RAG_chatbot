# generator.py
from langchain_openai import ChatOpenAI
import os
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from retriever import Retriever
from tools import get_summarize_tool, translate_text, search_web
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
import json

class Generator:
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.1):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        self.retriever = Retriever()

        self.tools = []
        self.build_dynamic_tools()
        
        self.tools.extend([get_summarize_tool(self.llm), translate_text, search_web])

        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True
        )

    def load_summary(self, index_name: str, file_json: str = "summaries.json") -> str:
        if os.path.exists(file_json):
            with open(file_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get(index_name, "Không có mô tả.")
        return "Không có mô tả cho tập tin này."

    # Hàm dùng để xây dựng các tool từ index
    def build_dynamic_tools(self):
        index_names = self.retriever.get_collection_names()

        for index_name in index_names:
            description = self.load_summary(index_name)  
            tool_func = self.create_index_tool(index_name)
            tool_obj = Tool(
                name=f"search_{index_name}",
                func=tool_func,
                description=description
            )
            self.tools.append(tool_obj)

    def create_index_tool(self, index_name: str):
        def search_fn(query: str) -> str:
            docs = self.retriever.search(index_name, query, top_k=5)
            return "\n\n".join([doc.page_content for doc in docs])
        return search_fn

    def save_summary(self, index_name: str, summary: str, file_json: str = "summaries.json"):
        data = {}
        if os.path.exists(file_json):
            with open(file_json, "r", encoding="utf-8") as f:
                data = json.load(f)

        data[index_name] = summary

        with open(file_json, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def summarize_and_save_tool(self, splitted_docs, index_name: str) -> str:
        # Gộp tóm tắt (map-reduce style)
        map_prompt = PromptTemplate.from_template(
            "Bạn là một trợ lý AI. Hãy đọc đoạn văn bản sau và rút ra nội dung chính theo phong cách mô tả tài liệu.\n"
            "Mục tiêu là giúp người dùng biết tài liệu này nói về điều gì, cung cấp những khái niệm, kiến thức hay thông tin gì, "
            "và tài liệu hữu ích trong trường hợp nào.\n\n"
            "Văn bản:\n{text}\n\nMô tả:"
        )

        combine_prompt = PromptTemplate.from_template(
            "Dưới đây là các mô tả được trích xuất từ nhiều đoạn của một tài liệu. Hãy tổng hợp thành một mô tả ngắn gọn, súc tích bằng tiếng Việt.\n"
            "Mô tả cần giúp người dùng biết nội dung chính của tài liệu, tài liệu dùng để làm gì, hoặc nên dùng khi nào.\n\n"
            "{text}\n\nTóm tắt mô tả cuối cùng:"
        )
        chain = load_summarize_chain(
            self.llm,
            chain_type="map_reduce",
            map_prompt=map_prompt,
            combine_prompt=combine_prompt,
            verbose=True
        )
        summary = chain.run(splitted_docs)

        # Lưu tóm tắt vào đúng folder index để tương thích với load_summary
        self.save_summary(index_name, summary)

        # Tạo function cho tool từ index_name
        tool_func = self.create_index_tool(index_name)

        # Tạo tool object từ function và summary
        tool_obj = Tool(
            name=f"search_{index_name}",
            func=tool_func,
            description=summary
        )

        # Thêm tool vào agent
        self.tools.append(tool_obj)

        # Cập nhật lại agent để nhận tool mới
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True
        )

    def generate_answer(self, question: str) -> str:
        response = self.agent.run(question)
        return response
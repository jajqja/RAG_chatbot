# chatbot.py
from generator import Generator
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

class Chatbot:
    def __init__(self):
        self.generator = Generator()

    def ask(self, question):
        answer = self.generator.generate_answer(question)
        return answer
    
    def split_uploaded_file(self, file, chunk_size:int = 800, chunk_overlap:int = 100):
        documents = []
        ext = os.path.splitext(file)[-1].lower()
        if ext == ".txt":
            loader = TextLoader(file, encoding="utf-8")
        elif ext == ".pdf":
            loader = PyPDFLoader(file)
        elif ext == ".docx":
            loader = Docx2txtLoader(file)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        documents.extend(loader.load())

        if not documents:
            return
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        docs = text_splitter.split_documents(documents)

        return docs
    
    def build_tool_and_index(self, uploaded_file):
        file_name = os.path.splitext(os.path.basename(uploaded_file))[0].lower()
        
        # Build index
        docs_for_RAG = self.split_uploaded_file(uploaded_file, 500, 50)
        self.generator.retriever.build_index(docs_for_RAG, file_name)
        
        # Build tool
        docs_for_summarize = self.split_uploaded_file(uploaded_file, 800, 100)
        self.generator.summarize_and_save_tool(docs_for_summarize, file_name)
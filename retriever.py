from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import os

class Retriever:
    def __init__(self, 
                 data_folder: str = "data/docs"):
        self.data_folder = data_folder

        self.embeddings = OpenAIEmbeddings(openai_api_key= os.getenv("OPENAI_API_KEY"))

        self.client = QdrantClient(
            url="https://025ca00e-a260-453e-89d3-5789a2e9d102.us-east4-0.gcp.cloud.qdrant.io:6333",
            api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.fHs4XmewmlEJ09WkweJ_Uvsf3eL_f4oxJmcI0CgtnZs"
        )
    
    def create_collection(self, collection_name, dim=1536):
        self.client.recreate_collection(
            collection_name=collection_name,
            vectors_config= VectorParams(size=dim, distance=Distance.COSINE)
        )


    def build_index(self, splitted_docs, idx_name):
        docs = [Document(page_content=doc.page_content, metadata=doc.metadata) for doc in splitted_docs]
        self.create_collection(idx_name)
        db = Qdrant(
            client=self.client,
            collection_name=idx_name,
            embeddings=self.embeddings
        )
        db.add_documents(docs)
        

    def search(self, collection_name, query: str, top_k: int):
        db = Qdrant(
            client=self.client,
            collection_name=collection_name,
            embeddings=self.embeddings
        )
        retriever = db.as_retriever(search_kwargs={"k": top_k})
        return retriever.get_relevant_documents(query)
    
        
    def get_collection_names(self):
        collection_names = self.client.get_collections().collections
        return [c.name for c in collection_names]

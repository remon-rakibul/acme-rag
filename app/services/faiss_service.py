import os
from typing import List, Tuple, Optional
import asyncio
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from app.services.logging_service import logger

STORAGE_DIR = "data"
FAISS_STORAGE_DIR = os.path.join(STORAGE_DIR, "faiss_index")


class FAISSService:
    def __init__(self):
        self.vectorstore: Optional[FAISS] = None
        self._index_loaded = False
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        os.makedirs(FAISS_STORAGE_DIR, exist_ok=True)
    
    def _get_embeddings(self):
        return HuggingFaceEmbeddings(
            model_name="paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'}
        )
    
    def _load_index(self):
        if self._index_loaded:
            return
        
        if os.path.exists(FAISS_STORAGE_DIR) and os.listdir(FAISS_STORAGE_DIR):
            try:
                embeddings = self._get_embeddings()
                self.vectorstore = FAISS.load_local(
                    FAISS_STORAGE_DIR,
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"Loaded FAISS index with {len(self.vectorstore.docstore._dict)} documents")
                self._index_loaded = True
            except Exception as e:
                logger.warning(f"Error loading index: {e}. Creating new index.")
                self._create_new_index()
                self._index_loaded = True
        else:
            self._create_new_index()
            self._index_loaded = True
    
    def _create_new_index(self):
        self.vectorstore = None
    
    async def add_documents_from_langchain(self, documents: List[Document]):
        if not documents:
            return
        
        if not self._index_loaded:
            self._load_index()
        
        for doc in documents:
            doc.metadata["length"] = len(doc.page_content)
        
        loop = asyncio.get_event_loop()
        embeddings = self._get_embeddings()
        
        if self.vectorstore is None or len(self.vectorstore.docstore._dict) == 0:
            self.vectorstore = await loop.run_in_executor(
                None, FAISS.from_documents, documents, embeddings
            )
        else:
            await loop.run_in_executor(
                None, self.vectorstore.add_documents, documents
            )
        
        await loop.run_in_executor(None, self._save_index)
        logger.info(f"Added {len(documents)} documents to index. Total: {len(self.vectorstore.docstore._dict)}")
    
    async def search(self, query: str, top_k: int = 3) -> List[Tuple[dict, float]]:
        if not self._index_loaded:
            self._load_index()
        
        if self.vectorstore is None or len(self.vectorstore.docstore._dict) == 0:
            return []
        
        loop = asyncio.get_event_loop()
        docs_with_scores = await loop.run_in_executor(
            None, self.vectorstore.similarity_search_with_score, query, top_k
        )
        
        return [
            (
                {
                    "id": hash(doc.page_content) % 1000000,
                    "text": doc.page_content,
                    "language": doc.metadata.get("language", "en"),
                    "filename": doc.metadata.get("filename", "unknown"),
                    "length": len(doc.page_content)
                },
                1.0 / (1.0 + float(score))
            )
            for doc, score in docs_with_scores
        ]
    
    def _save_index(self):
        try:
            if self.vectorstore:
                self.vectorstore.save_local(FAISS_STORAGE_DIR)
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def get_stats(self) -> dict:
        if not self._index_loaded:
            self._load_index()
        
        total_docs = len(self.vectorstore.docstore._dict) if self.vectorstore else 0
        
        return {
            "total_documents": total_docs,
            "dimension": 384,
            "index_type": "FAISS (LangChain)"
        }


faiss_service = FAISSService()

"""
RAG Pipeline برای یادگیری API و مستندات
استفاده از drf-spectacular برای تولید OpenAPI schema و پردازش آن با LangChain
"""

import os
import json
from pathlib import Path
from typing import List, Optional
from django.conf import settings
from django.core.management import call_command
from io import StringIO


class RAGPipeline:
    """کلاس برای مدیریت RAG pipeline"""
    
    def __init__(self, schema_path: Optional[str] = None, vector_store_path: Optional[str] = None):
        """
        Args:
            schema_path: مسیر فایل OpenAPI schema (اختیاری)
            vector_store_path: مسیر ذخیره vector store (اختیاری)
        """
        self.schema_path = schema_path or os.path.join(settings.BASE_DIR, 'schema.yaml')
        self.vector_store_path = vector_store_path or os.path.join(settings.BASE_DIR, 'chroma_db')
        self.vector_store = None
        self.retriever = None
    
    def generate_schema(self) -> str:
        """
        تولید OpenAPI schema با استفاده از drf-spectacular
        
        Returns:
            مسیر فایل schema تولید شده
        """
        try:
            # اجرای دستور spectacular برای تولید schema
            output = StringIO()
            call_command('spectacular', '--file', self.schema_path, '--format', 'openapi-json', stdout=output)
            
            if os.path.exists(self.schema_path):
                return self.schema_path
            else:
                raise FileNotFoundError(f"Schema file not created at {self.schema_path}")
        except Exception as e:
            raise Exception(f"Error generating schema: {str(e)}")
    
    def load_schema(self) -> List:
        """
        بارگذاری و پردازش OpenAPI schema با LangChain
        
        Returns:
            لیست Document objects
        """
        try:
            from langchain.document_loaders import OpenAPISpecLoader
            
            # بررسی وجود فایل schema
            if not os.path.exists(self.schema_path):
                # اگر وجود ندارد، تولید کن
                self.generate_schema()
            
            # بارگذاری schema
            loader = OpenAPISpecLoader(self.schema_path)
            documents = loader.load()
            
            return documents
        except ImportError:
            raise ImportError("langchain is not installed. Install it with: pip install langchain")
        except Exception as e:
            raise Exception(f"Error loading schema: {str(e)}")
    
    def create_embeddings(self, use_huggingface: bool = True, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        ایجاد embeddings و ذخیره در vector store
        
        Args:
            use_huggingface: استفاده از Hugging Face برای embeddings (کاهش هزینه)
            model_name: نام مدل برای embeddings
        """
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            from langchain.vectorstores import Chroma
            
            # بارگذاری documents
            documents = self.load_schema()
            
            # تقسیم به chunkهای کوچک‌تر
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(documents)
            
            # ایجاد embeddings
            if use_huggingface:
                from langchain_huggingface import HuggingFaceEmbeddings
                embeddings = HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs={'device': 'cpu'}
                )
            else:
                from langchain_openai import OpenAIEmbeddings
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    raise ValueError("OPENAI_API_KEY is required for OpenAI embeddings")
                embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            
            # ایجاد vector store
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=self.vector_store_path
            )
            
            # ایجاد retriever
            self.retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 3}
            )
            
            return self.vector_store
        
        except ImportError as e:
            raise ImportError(f"Required package not installed: {str(e)}")
        except Exception as e:
            raise Exception(f"Error creating embeddings: {str(e)}")
    
    def get_retriever(self):
        """
        دریافت retriever برای استفاده در Agent
        
        Returns:
            Retriever instance
        """
        if not self.retriever:
            # اگر retriever وجود ندارد، ایجاد کن
            self.create_embeddings()
        
        return self.retriever
    
    def search(self, query: str, k: int = 3) -> List:
        """
        جستجو در مستندات
        
        Args:
            query: متن جستجو
            k: تعداد نتایج
        
        Returns:
            لیست نتایج مرتبط
        """
        if not self.retriever:
            self.get_retriever()
        
        return self.retriever.get_relevant_documents(query)
    
    def reload(self):
        """بارگذاری مجدد schema و به‌روزرسانی vector store"""
        # حذف vector store قدیمی
        if os.path.exists(self.vector_store_path):
            import shutil
            shutil.rmtree(self.vector_store_path)
        
        # تولید schema جدید
        self.generate_schema()
        
        # ایجاد embeddings جدید
        self.create_embeddings()


def get_rag_pipeline() -> RAGPipeline:
    """
    Factory function برای دریافت RAG pipeline instance
    
    Returns:
        RAGPipeline instance
    """
    return RAGPipeline()


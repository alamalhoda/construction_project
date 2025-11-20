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
        self.schema_path = schema_path or os.path.join(settings.BASE_DIR, 'schema.json')
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
            # در langchain 1.0، OpenAPISpecLoader حذف شده است
            # استفاده از روش جایگزین: بارگذاری مستقیم JSON schema
            from langchain_core.documents import Document
            
            # بررسی وجود فایل schema
            if not os.path.exists(self.schema_path):
                # اگر وجود ندارد، تولید کن
                self.generate_schema()
            
            # بارگذاری schema به صورت مستقیم
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
            
            # تبدیل به Document objects
            documents = []
            # پردازش paths
            if 'paths' in schema_data:
                for path, methods in schema_data['paths'].items():
                    for method, details in methods.items():
                        if isinstance(details, dict):
                            summary = details.get('summary', '')
                            description = details.get('description', '')
                            content = f"Endpoint: {method.upper()} {path}\nSummary: {summary}\nDescription: {description}"
                            documents.append(Document(page_content=content, metadata={"path": path, "method": method}))
            
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
        
        Returns:
            VectorStore instance یا None در صورت خطا
        """
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            from langchain_community.vectorstores import Chroma
            
            # بارگذاری documents
            documents = self.load_schema()
            
            if not documents:
                print("Warning: No documents found in schema")
                return None
            
            # تقسیم به chunkهای کوچک‌تر
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(documents)
            
            # ایجاد embeddings
            embeddings = None
            if use_huggingface:
                try:
                    from langchain_huggingface import HuggingFaceEmbeddings
                    embeddings = HuggingFaceEmbeddings(
                        model_name=model_name,
                        model_kwargs={'device': 'cpu'}
                    )
                except ImportError as e:
                    print(f"Warning: Hugging Face embeddings not available: {str(e)}")
                    print("   Trying OpenAI embeddings instead...")
                    use_huggingface = False
            
            if not embeddings and not use_huggingface:
                try:
                    from langchain_openai import OpenAIEmbeddings
                    api_key = os.getenv('OPENAI_API_KEY')
                    if not api_key:
                        print("Warning: OPENAI_API_KEY not found. RAG will be disabled.")
                        return None
                    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
                except ImportError:
                    print("Warning: OpenAI embeddings not available. RAG will be disabled.")
                    return None
            
            if not embeddings:
                print("Warning: No embeddings available. RAG will be disabled.")
                return None
            
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
            print(f"Warning: Required package not installed: {str(e)}")
            print("   RAG will be disabled. To enable RAG, install required packages:")
            print("   - For Hugging Face: pip install sentence-transformers torch")
            print("   - For OpenAI: Set OPENAI_API_KEY environment variable")
            return None
        except Exception as e:
            print(f"Warning: Error creating embeddings: {str(e)}")
            print("   RAG will be disabled.")
            return None
    
    def get_retriever(self):
        """
        دریافت retriever برای استفاده در Agent
        
        Returns:
            Retriever instance یا None در صورت خطا
        """
        if not self.retriever:
            # اگر retriever وجود ندارد، ایجاد کن
            # اما ابتدا بررسی می‌کنیم که آیا embeddings در دسترس است
            try:
                vector_store = self.create_embeddings()
                if not vector_store:
                    print("Warning: Could not create embeddings. RAG will be disabled.")
                    return None
            except Exception as e:
                print(f"Warning: Error creating embeddings: {str(e)}")
                print("   RAG will be disabled.")
                return None
        
        return self.retriever
    
    def search(self, query: str, k: int = 3) -> List:
        """
        جستجو در مستندات
        
        Args:
            query: متن جستجو
            k: تعداد نتایج
        
        Returns:
            لیست نتایج مرتبط یا لیست خالی در صورت خطا
        """
        if not self.retriever:
            self.retriever = self.get_retriever()
        
        if not self.retriever:
            return []
        
        try:
            return self.retriever.get_relevant_documents(query)
        except Exception as e:
            print(f"Warning: Error searching in RAG: {str(e)}")
            return []
    
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


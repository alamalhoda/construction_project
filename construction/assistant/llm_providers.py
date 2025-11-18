"""
LLM Provider Abstraction Layer
پشتیبانی از چندین LLM provider شامل OpenAI, Anthropic, Hugging Face, Google Gemini, OpenRouter و Local models
"""

import os
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from django.conf import settings


class LLMProvider(ABC):
    """Base class برای تمام LLM providers"""
    
    @abstractmethod
    def get_llm(self, **kwargs):
        """ایجاد و برگرداندن LLM instance"""
        pass
    
    @abstractmethod
    def supports_function_calling(self) -> bool:
        """بررسی اینکه آیا این provider از Function Calling پشتیبانی می‌کند"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """دریافت نام مدل"""
        pass


class OpenAIProvider(LLMProvider):
    """Provider برای OpenAI GPT models"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    def get_llm(self, temperature: float = 0, **kwargs):
        """ایجاد OpenAI LLM"""
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model_name=self.model,
                temperature=temperature,
                openai_api_key=self.api_key,
                **kwargs
            )
        except ImportError:
            raise ImportError("langchain-openai is not installed. Install it with: pip install langchain-openai")
    
    def supports_function_calling(self) -> bool:
        return True
    
    def get_model_name(self) -> str:
        return f"OpenAI {self.model}"


class AnthropicProvider(LLMProvider):
    """Provider برای Anthropic Claude models"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.model = model
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
    def get_llm(self, temperature: float = 0, **kwargs):
        """ایجاد Anthropic LLM"""
        try:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=self.model,
                temperature=temperature,
                anthropic_api_key=self.api_key,
                **kwargs
            )
        except ImportError:
            raise ImportError("langchain-anthropic is not installed. Install it with: pip install langchain-anthropic")
    
    def supports_function_calling(self) -> bool:
        return True
    
    def get_model_name(self) -> str:
        return f"Anthropic {self.model}"


class HuggingFaceProvider(LLMProvider):
    """Provider برای Hugging Face models (از طریق Spaces یا Inference API)"""
    
    def __init__(self, model_id: str, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        """
        Args:
            model_id: شناسه مدل در Hugging Face (مثلاً 'mistralai/Mistral-7B-Instruct-v0.2')
            api_key: API key برای Hugging Face (اختیاری)
            endpoint: URL endpoint برای Hugging Face Space (اختیاری)
        """
        self.model_id = model_id
        self.api_key = api_key or os.getenv('HUGGINGFACE_API_KEY')
        self.endpoint = endpoint or os.getenv('HUGGINGFACE_ENDPOINT')
    
    def get_llm(self, temperature: float = 0, **kwargs):
        """ایجاد Hugging Face LLM"""
        try:
            from langchain_huggingface import HuggingFaceEndpoint
            
            if self.endpoint:
                # استفاده از Hugging Face Space endpoint
                return HuggingFaceEndpoint(
                    endpoint_url=self.endpoint,
                    huggingfacehub_api_token=self.api_key,
                    temperature=temperature,
                    **kwargs
                )
            else:
                # استفاده از Inference API
                return HuggingFaceEndpoint(
                    repo_id=self.model_id,
                    huggingfacehub_api_token=self.api_key,
                    temperature=temperature,
                    **kwargs
                )
        except ImportError:
            raise ImportError("langchain-huggingface is not installed. Install it with: pip install langchain-huggingface")
    
    def supports_function_calling(self) -> bool:
        # Hugging Face models معمولاً از Function Calling پشتیبانی نمی‌کنند
        return False
    
    def get_model_name(self) -> str:
        return f"HuggingFace {self.model_id}"


class GoogleGeminiProvider(LLMProvider):
    """Provider برای Google Gemini models"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        """
        Args:
            api_key: API key برای Google Gemini
            model: نام مدل (gemini-pro, gemini-pro-vision, gemini-1.5-pro, etc.)
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        self.model = model
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable is required")
    
    def get_llm(self, temperature: float = 0, **kwargs):
        """ایجاد Google Gemini LLM"""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            return ChatGoogleGenerativeAI(
                model=self.model,
                temperature=temperature,
                google_api_key=self.api_key,
                **kwargs
            )
        except ImportError:
            raise ImportError("langchain-google-genai is not installed. Install it with: pip install langchain-google-genai")
    
    def supports_function_calling(self) -> bool:
        # Google Gemini از Function Calling پشتیبانی می‌کند
        return True
    
    def get_model_name(self) -> str:
        return f"Google Gemini {self.model}"


class OpenRouterProvider(LLMProvider):
    """Provider برای OpenRouter (unified interface for multiple LLMs)"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Args:
            api_key: API key برای OpenRouter
            model: نام مدل در OpenRouter (مثلاً 'openai/gpt-4', 'anthropic/claude-3-sonnet', 'google/gemini-pro')
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.model = model or os.getenv('OPENROUTER_MODEL', 'openai/gpt-4')
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
    
    def get_llm(self, temperature: float = 0, **kwargs):
        """ایجاد OpenRouter LLM"""
        try:
            from langchain_openai import ChatOpenAI
            
            # OpenRouter با OpenAI API compatible است
            return ChatOpenAI(
                model=self.model,
                temperature=temperature,
                openai_api_key=self.api_key,
                base_url=self.base_url,
                default_headers={
                    "HTTP-Referer": os.getenv('OPENROUTER_HTTP_REFERER', 'https://github.com/your-repo'),
                    "X-Title": os.getenv('OPENROUTER_X_TITLE', 'Construction Project Assistant'),
                },
                **kwargs
            )
        except ImportError:
            raise ImportError("langchain-openai is not installed. Install it with: pip install langchain-openai")
    
    def supports_function_calling(self) -> bool:
        # بستگی به مدل انتخابی دارد، اما اکثر مدل‌های معروف پشتیبانی می‌کنند
        return True
    
    def get_model_name(self) -> str:
        return f"OpenRouter {self.model}"


class LocalModelProvider(LLMProvider):
    """Provider برای مدل‌های محلی (Ollama, LocalAI)"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        """
        Args:
            base_url: URL پایه برای Ollama یا LocalAI
            model: نام مدل
        """
        self.base_url = base_url or os.getenv('LOCAL_MODEL_URL', 'http://localhost:11434')
        self.model = model
    
    def get_llm(self, temperature: float = 0, **kwargs):
        """ایجاد Local LLM"""
        try:
            from langchain_community.llms import Ollama
            
            return Ollama(
                base_url=self.base_url,
                model=self.model,
                temperature=temperature,
                **kwargs
            )
        except ImportError:
            raise ImportError("langchain-community is not installed. Install it with: pip install langchain-community")
    
    def supports_function_calling(self) -> bool:
        # بستگی به مدل دارد، اما معمولاً پشتیبانی نمی‌کند
        return False
    
    def get_model_name(self) -> str:
        return f"Local {self.model}"


class LLMProviderFactory:
    """Factory برای ایجاد LLM providers"""
    
    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> LLMProvider:
        """
        ایجاد provider بر اساس نوع
        
        Args:
            provider_type: نوع provider ('openai', 'anthropic', 'huggingface', 'gemini', 'openrouter', 'local')
            **kwargs: پارامترهای اضافی برای provider
        
        Returns:
            LLMProvider instance
        """
        provider_type = provider_type.lower()
        
        if provider_type == 'openai':
            return OpenAIProvider(**kwargs)
        elif provider_type == 'anthropic':
            return AnthropicProvider(**kwargs)
        elif provider_type == 'huggingface':
            return HuggingFaceProvider(**kwargs)
        elif provider_type == 'gemini' or provider_type == 'google':
            return GoogleGeminiProvider(**kwargs)
        elif provider_type == 'openrouter':
            return OpenRouterProvider(**kwargs)
        elif provider_type == 'local':
            return LocalModelProvider(**kwargs)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}. Supported types: openai, anthropic, huggingface, gemini, openrouter, local")
    
    @staticmethod
    def get_default_provider() -> LLMProvider:
        """
        دریافت provider پیش‌فرض از تنظیمات
        
        Returns:
            LLMProvider instance
        """
        provider_type = getattr(settings, 'AI_ASSISTANT_PROVIDER', 'openai').lower()
        provider_config = getattr(settings, 'AI_ASSISTANT_PROVIDER_CONFIG', {})
        
        return LLMProviderFactory.create_provider(provider_type, **provider_config)


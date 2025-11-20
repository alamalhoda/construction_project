#!/usr/bin/env python3
"""
اسکریپت جامع برای تست دسترسی به مدل‌های مختلف از providerهای مختلف
این اسکریپت دسترسی به مدل‌های رایگان و غیر رایگان را بررسی می‌کند
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List, Tuple

# لود کردن متغیرهای محیطی
load_dotenv()

# رنگ‌ها برای خروجی
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """چاپ هدر با فرمت زیبا"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}\n")

def print_success(text: str):
    """چاپ پیام موفقیت"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str):
    """چاپ پیام خطا"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text: str):
    """چاپ پیام هشدار"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text: str):
    """چاپ اطلاعات"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

# نتایج تست
results = {
    'google': {'free': [], 'paid': [], 'errors': []},
    'openai': {'free': [], 'paid': [], 'errors': []},
    'openrouter': {'free': [], 'paid': [], 'errors': []},
    'huggingface': {'free': [], 'paid': [], 'errors': []},
}

def test_google_gemini():
    """تست مدل‌های Google Gemini"""
    print_header("🔍 تست Google Gemini")
    
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print_error("GOOGLE_API_KEY یا GEMINI_API_KEY یافت نشد!")
        results['google']['errors'].append("API key not found")
        return
    
    print_success(f"API Key found: {api_key[:20]}...")
    
    # مدل‌های رایگان احتمالی
    free_models = [
        'gemini-2.0-flash',
        'gemini-2.0-flash-001',
        'gemini-2.5-flash',
        'gemini-flash-latest',
        'gemini-2.0-flash-lite',
        'gemini-2.0-flash-lite-001',
    ]
    
    # مدل‌های پولی احتمالی
    paid_models = [
        'gemini-2.5-pro',
        'gemini-2.0-pro-exp',
        'gemini-3-pro-preview',
    ]
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # تست مدل‌های رایگان
        print_info("تست مدل‌های رایگان...")
        for model_name in free_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("test")
                print_success(f"{model_name} - کار می‌کند (رایگان)")
                results['google']['free'].append(model_name)
            except Exception as e:
                error_msg = str(e)
                if 'quota' in error_msg.lower() or 'billing' in error_msg.lower():
                    print_warning(f"{model_name} - نیاز به پرداخت")
                    results['google']['paid'].append(model_name)
                elif 'location' in error_msg.lower() or 'not supported' in error_msg.lower():
                    print_error(f"{model_name} - منطقه جغرافیایی پشتیبانی نمی‌شود (تحریم)")
                    results['google']['errors'].append(f"{model_name}: Location not supported")
                elif '404' in error_msg or 'not found' in error_msg.lower():
                    print_error(f"{model_name} - پیدا نشد")
                    results['google']['errors'].append(f"{model_name}: Not found")
                else:
                    print_error(f"{model_name} - خطا: {error_msg[:100]}")
                    results['google']['errors'].append(f"{model_name}: {error_msg[:100]}")
        
        # تست مدل‌های پولی
        print_info("تست مدل‌های پولی...")
        for model_name in paid_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("test")
                print_success(f"{model_name} - کار می‌کند")
                results['google']['paid'].append(model_name)
            except Exception as e:
                error_msg = str(e)
                if 'quota' in error_msg.lower() or 'billing' in error_msg.lower():
                    print_warning(f"{model_name} - نیاز به پرداخت")
                    results['google']['paid'].append(f"{model_name} (needs payment)")
                else:
                    print_error(f"{model_name} - خطا: {error_msg[:100]}")
                    results['google']['errors'].append(f"{model_name}: {error_msg[:100]}")
                    
    except ImportError:
        print_error("google-generativeai نصب نشده است! (pip install google-generativeai)")
        results['google']['errors'].append("Package not installed")
    except Exception as e:
        print_error(f"خطای کلی: {str(e)}")
        results['google']['errors'].append(f"General error: {str(e)}")

def test_openai():
    """تست مدل‌های OpenAI"""
    print_header("🔍 تست OpenAI")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print_error("OPENAI_API_KEY یافت نشد!")
        results['openai']['errors'].append("API key not found")
        return
    
    print_success(f"API Key found: {api_key[:20]}...")
    
    # مدل‌های رایگان احتمالی (معمولاً همه پولی هستند)
    free_models = []  # OpenAI معمولاً رایگان ندارد
    
    # مدل‌های پولی
    paid_models = [
        'gpt-4o-mini',
        'gpt-4o',
        'gpt-4-turbo',
        'gpt-4',
        'gpt-3.5-turbo',
    ]
    
    try:
        from langchain_openai import ChatOpenAI
        
        # تست مدل‌های پولی
        print_info("تست مدل‌های OpenAI...")
        for model_name in paid_models:
            try:
                llm = ChatOpenAI(
                    model=model_name,
                    openai_api_key=api_key,
                    temperature=0,
                    max_tokens=10  # کم کردن tokens برای تست
                )
                response = llm.invoke("test")
                print_success(f"{model_name} - کار می‌کند")
                results['openai']['paid'].append(model_name)
            except Exception as e:
                error_msg = str(e)
                if 'quota' in error_msg.lower() or 'insufficient_quota' in error_msg.lower():
                    print_warning(f"{model_name} - quota تمام شده")
                    results['openai']['errors'].append(f"{model_name}: Quota exceeded")
                elif '401' in error_msg or 'auth' in error_msg.lower():
                    print_error(f"{model_name} - مشکل احراز هویت")
                    results['openai']['errors'].append(f"{model_name}: Authentication error")
                elif '429' in error_msg:
                    print_warning(f"{model_name} - rate limit")
                    results['openai']['errors'].append(f"{model_name}: Rate limit")
                else:
                    print_error(f"{model_name} - خطا: {error_msg[:100]}")
                    results['openai']['errors'].append(f"{model_name}: {error_msg[:100]}")
                    
    except ImportError:
        print_error("langchain-openai نصب نشده است! (pip install langchain-openai)")
        results['openai']['errors'].append("Package not installed")
    except Exception as e:
        print_error(f"خطای کلی: {str(e)}")
        results['openai']['errors'].append(f"General error: {str(e)}")

def test_openrouter():
    """تست مدل‌های OpenRouter"""
    print_header("🔍 تست OpenRouter")
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print_error("OPENROUTER_API_KEY یافت نشد!")
        results['openrouter']['errors'].append("API key not found")
        return
    
    print_success(f"API Key found: {api_key[:20]}...")
    
    # مدل‌های رایگان
    free_models = [
        'google/gemini-2.0-flash-exp:free',
        'z-ai/glm-4.5-air:free',
        'google/gemini-2.0-flash-exp:free',
    ]
    
    # مدل‌های پولی
    paid_models = [
        'openai/gpt-4o-mini',
        'openai/gpt-4o',
        'anthropic/claude-3-sonnet',
    ]
    
    try:
        from langchain_openai import ChatOpenAI
        
        # تست مدل‌های رایگان
        print_info("تست مدل‌های رایگان...")
        for model_name in free_models:
            try:
                llm = ChatOpenAI(
                    model=model_name,
                    openai_api_key=api_key,
                    base_url="https://openrouter.ai/api/v1",
                    temperature=0,
                    max_tokens=10
                )
                response = llm.invoke("test")
                print_success(f"{model_name} - کار می‌کند (رایگان)")
                results['openrouter']['free'].append(model_name)
            except Exception as e:
                error_msg = str(e)
                if '429' in error_msg or 'rate limit' in error_msg.lower():
                    print_warning(f"{model_name} - rate limit (محدودیت روزانه)")
                    results['openrouter']['errors'].append(f"{model_name}: Rate limit")
                elif '402' in error_msg or 'credit' in error_msg.lower():
                    print_warning(f"{model_name} - نیاز به credit")
                    results['openrouter']['paid'].append(model_name)
                elif '401' in error_msg or 'auth' in error_msg.lower():
                    print_error(f"{model_name} - مشکل احراز هویت")
                    results['openrouter']['errors'].append(f"{model_name}: Authentication error")
                else:
                    print_error(f"{model_name} - خطا: {error_msg[:100]}")
                    results['openrouter']['errors'].append(f"{model_name}: {error_msg[:100]}")
        
        # تست مدل‌های پولی
        print_info("تست مدل‌های پولی...")
        for model_name in paid_models:
            try:
                llm = ChatOpenAI(
                    model=model_name,
                    openai_api_key=api_key,
                    base_url="https://openrouter.ai/api/v1",
                    temperature=0,
                    max_tokens=10
                )
                response = llm.invoke("test")
                print_success(f"{model_name} - کار می‌کند")
                results['openrouter']['paid'].append(model_name)
            except Exception as e:
                error_msg = str(e)
                if '402' in error_msg or 'credit' in error_msg.lower():
                    print_warning(f"{model_name} - نیاز به credit")
                    results['openrouter']['paid'].append(f"{model_name} (needs credit)")
                else:
                    print_error(f"{model_name} - خطا: {error_msg[:100]}")
                    results['openrouter']['errors'].append(f"{model_name}: {error_msg[:100]}")
                    
    except ImportError:
        print_error("langchain-openai نصب نشده است! (pip install langchain-openai)")
        results['openrouter']['errors'].append("Package not installed")
    except Exception as e:
        print_error(f"خطای کلی: {str(e)}")
        results['openrouter']['errors'].append(f"General error: {str(e)}")

def test_huggingface():
    """تست مدل‌های Hugging Face"""
    print_header("🔍 تست Hugging Face")
    
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    endpoint = os.getenv('HUGGINGFACE_ENDPOINT')
    model_id = os.getenv('HUGGINGFACE_MODEL_ID', 'mistralai/Mistral-7B-Instruct-v0.2')
    
    if not api_key and not endpoint:
        print_warning("HUGGINGFACE_API_KEY یا HUGGINGFACE_ENDPOINT یافت نشد!")
        print_info("Hugging Face معمولاً رایگان است اما نیاز به نصب sentence-transformers دارد")
        results['huggingface']['errors'].append("API key/endpoint not found")
        return
    
    if api_key:
        print_success(f"API Key found: {api_key[:20]}...")
    if endpoint:
        print_success(f"Endpoint found: {endpoint}")
    
    try:
        from langchain_huggingface import HuggingFaceEndpoint
        
        # تست با endpoint
        if endpoint:
            try:
                llm = HuggingFaceEndpoint(
                    endpoint_url=endpoint,
                    huggingfacehub_api_token=api_key,
                    temperature=0,
                    max_new_tokens=10
                )
                response = llm.invoke("test")
                print_success(f"Endpoint {endpoint} - کار می‌کند (رایگان)")
                results['huggingface']['free'].append(f"Endpoint: {endpoint}")
            except Exception as e:
                error_msg = str(e)
                print_error(f"Endpoint - خطا: {error_msg[:100]}")
                results['huggingface']['errors'].append(f"Endpoint: {error_msg[:100]}")
        
        # تست با model_id
        if model_id:
            try:
                llm = HuggingFaceEndpoint(
                    repo_id=model_id,
                    huggingfacehub_api_token=api_key,
                    temperature=0,
                    max_new_tokens=10
                )
                response = llm.invoke("test")
                print_success(f"Model {model_id} - کار می‌کند (رایگان)")
                results['huggingface']['free'].append(f"Model: {model_id}")
            except Exception as e:
                error_msg = str(e)
                print_error(f"Model {model_id} - خطا: {error_msg[:100]}")
                results['huggingface']['errors'].append(f"{model_id}: {error_msg[:100]}")
                
    except ImportError:
        print_error("langchain-huggingface نصب نشده است! (pip install langchain-huggingface)")
        print_info("یا می‌توانید از sentence-transformers برای استفاده محلی استفاده کنید")
        results['huggingface']['errors'].append("Package not installed")
    except Exception as e:
        print_error(f"خطای کلی: {str(e)}")
        results['huggingface']['errors'].append(f"General error: {str(e)}")

def print_summary():
    """چاپ خلاصه نتایج"""
    print_header("📊 خلاصه نتایج")
    
    for provider, data in results.items():
        provider_name = provider.upper()
        print(f"\n{Colors.BOLD}{provider_name}:{Colors.RESET}")
        
        if data['free']:
            print(f"  {Colors.GREEN}✅ مدل‌های رایگان کارآمد ({len(data['free'])}):{Colors.RESET}")
            for model in data['free']:
                print(f"    • {model}")
        
        if data['paid']:
            print(f"  {Colors.YELLOW}💰 مدل‌های پولی ({len(data['paid'])}):{Colors.RESET}")
            for model in data['paid']:
                print(f"    • {model}")
        
        if data['errors']:
            print(f"  {Colors.RED}❌ خطاها ({len(data['errors'])}):{Colors.RESET}")
            for error in data['errors']:
                print(f"    • {error}")
        
        if not data['free'] and not data['paid'] and not data['errors']:
            print(f"  {Colors.YELLOW}⚠️  تست نشده{Colors.RESET}")
    
    # پیشنهادات
    print(f"\n{Colors.BOLD}{Colors.BLUE}💡 پیشنهادات:{Colors.RESET}")
    
    # پیدا کردن بهترین گزینه
    best_options = []
    for provider, data in results.items():
        if data['free']:
            best_options.append((provider, data['free'][0]))
    
    if best_options:
        print(f"\n  {Colors.GREEN}✅ بهترین گزینه‌های رایگان:{Colors.RESET}")
        for provider, model in best_options:
            print(f"    • {provider.upper()}: {model}")
    else:
        print(f"\n  {Colors.YELLOW}⚠️  هیچ مدل رایگانی کار نمی‌کند!{Colors.RESET}")
        print(f"  {Colors.YELLOW}   ممکن است نیاز به VPN باشد یا API key معتبر نیست{Colors.RESET}")

def main():
    """تابع اصلی"""
    print_header("🧪 تست دسترسی به مدل‌های مختلف")
    print(f"زمان تست: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # تست Google Gemini
    test_google_gemini()
    
    # تست OpenAI
    test_openai()
    
    # تست OpenRouter
    test_openrouter()
    
    # تست Hugging Face
    test_huggingface()
    
    # چاپ خلاصه
    print_summary()
    
    print_header("✅ تست کامل شد!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  تست توسط کاربر متوقف شد!")
        sys.exit(1)
    except Exception as e:
        print_error(f"خطای غیرمنتظره: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


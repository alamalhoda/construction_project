#!/usr/bin/env python3
"""
اسکریپت تست جامع برای بررسی وضعیت تمام مدل‌های LLM
این اسکریپت تمام provider های موجود را تست می‌کند و وضعیت آن‌ها را گزارش می‌دهد.
"""

import os
import sys
from dotenv import load_dotenv
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# بارگذاری متغیرهای محیطی از .env
load_dotenv()

# اضافه کردن مسیر پروژه به sys.path برای import کردن ماژول‌ها
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# تنظیم Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')

try:
    import django
    django.setup()
except Exception as e:
    print(f"⚠️  هشدار: نتوانست Django را راه‌اندازی کنم: {e}")
    print("   برخی تست‌ها ممکن است کار نکنند.")

from construction.assistant.llm_providers import LLMProviderFactory


class Colors:
    """کلاس برای رنگ‌های ترمینال"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class LLMTester:
    """کلاس اصلی برای تست LLM providers"""
    
    def __init__(self):
        self.results: List[Dict] = []
        self.test_message = "سلام! لطفاً فقط کلمه 'موفق' را برگردان."
    
    def print_header(self, text: str):
        """چاپ هدر با رنگ"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")
    
    def print_success(self, text: str):
        """چاپ پیام موفقیت"""
        print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")
    
    def print_error(self, text: str):
        """چاپ پیام خطا"""
        print(f"{Colors.RED}❌ {text}{Colors.RESET}")
    
    def print_warning(self, text: str):
        """چاپ پیام هشدار"""
        print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")
    
    def print_info(self, text: str):
        """چاپ پیام اطلاعاتی"""
        print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")
    
    def mask_api_key(self, api_key: Optional[str]) -> str:
        """ماسک کردن API key برای نمایش امن"""
        if not api_key:
            return "یافت نشد"
        if len(api_key) < 10:
            return "***"
        return f"{api_key[:10]}...{api_key[-4:]}"
    
    def test_provider(self, provider_type: str, **kwargs) -> Dict:
        """
        تست یک provider خاص
        
        Args:
            provider_type: نوع provider ('openai', 'anthropic', 'huggingface', 'gemini', 'openrouter', 'local')
            **kwargs: پارامترهای اضافی برای provider
        
        Returns:
            دیکشنری شامل نتایج تست
        """
        result = {
            'provider': provider_type,
            'success': False,
            'error': None,
            'response': None,
            'model_name': None,
            'api_key': None,
            'test_time': None
        }
        
        start_time = datetime.now()
        
        try:
            print(f"\n{Colors.BOLD}🔍 تست Provider: {provider_type.upper()}{Colors.RESET}")
            print("-" * 70)
            
            # ایجاد provider
            provider = LLMProviderFactory.create_provider(provider_type, **kwargs)
            result['model_name'] = provider.get_model_name()
            
            # دریافت API key برای نمایش
            if hasattr(provider, 'api_key'):
                result['api_key'] = provider.api_key
                print(f"🔑 API Key: {self.mask_api_key(provider.api_key)}")
            
            if hasattr(provider, 'model'):
                print(f"🤖 مدل: {provider.model}")
            
            # تست ایجاد LLM
            print("🔄 در حال ایجاد LLM...")
            llm = provider.get_llm(temperature=0)
            
            # تست ارسال پیام
            print("📤 در حال ارسال پیام تست...")
            response = llm.invoke(self.test_message)
            
            # استخراج پاسخ
            if hasattr(response, 'content'):
                result['response'] = response.content
            elif isinstance(response, str):
                result['response'] = response
            else:
                result['response'] = str(response)
            
            end_time = datetime.now()
            result['test_time'] = (end_time - start_time).total_seconds()
            result['success'] = True
            
            self.print_success(f"تست موفق بود!")
            print(f"📝 پاسخ: {result['response']}")
            print(f"⏱️  زمان تست: {result['test_time']:.2f} ثانیه")
            
        except ValueError as e:
            # خطای مربوط به نبودن API key یا پارامترهای لازم
            result['error'] = str(e)
            result['test_time'] = (datetime.now() - start_time).total_seconds()
            self.print_warning(f"API key یا پارامترهای لازم یافت نشد: {str(e)}")
            
        except ImportError as e:
            # خطای مربوط به نبودن کتابخانه
            result['error'] = str(e)
            result['test_time'] = (datetime.now() - start_time).total_seconds()
            self.print_error(f"کتابخانه مورد نیاز نصب نشده: {str(e)}")
            
        except Exception as e:
            # سایر خطاها
            error_msg = str(e)
            result['error'] = error_msg
            result['test_time'] = (datetime.now() - start_time).total_seconds()
            
            # تحلیل خطا
            if "401" in error_msg or "Unauthorized" in error_msg or "Invalid API key" in error_msg:
                self.print_error("API key نامعتبر یا غیرفعال است!")
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                self.print_error("محدودیت نرخ درخواست! لطفاً چند لحظه صبر کنید.")
            elif "model" in error_msg.lower() and "not found" in error_msg.lower():
                self.print_error("مدل انتخابی یافت نشد!")
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                self.print_error("مشکل در اتصال به سرویس!")
            else:
                self.print_error(f"خطا: {error_msg}")
        
        return result
    
    def test_openai(self) -> Dict:
        """تست OpenAI"""
        api_key = os.getenv('OPENAI_API_KEY')
        model = os.getenv('OPENAI_MODEL', 'gpt-4')
        
        if not api_key:
            return {
                'provider': 'openai',
                'success': False,
                'error': 'OPENAI_API_KEY environment variable is required',
                'api_key': None
            }
        
        return self.test_provider('openai', api_key=api_key, model=model)
    
    def test_anthropic(self) -> Dict:
        """تست Anthropic"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        model = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
        
        if not api_key:
            return {
                'provider': 'anthropic',
                'success': False,
                'error': 'ANTHROPIC_API_KEY environment variable is required',
                'api_key': None
            }
        
        return self.test_provider('anthropic', api_key=api_key, model=model)
    
    def test_google_gemini(self) -> Dict:
        """تست Google Gemini"""
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        model = os.getenv('GEMINI_MODEL', 'gemini-pro')
        
        if not api_key:
            return {
                'provider': 'gemini',
                'success': False,
                'error': 'GOOGLE_API_KEY or GEMINI_API_KEY environment variable is required',
                'api_key': None
            }
        
        return self.test_provider('gemini', api_key=api_key, model=model)
    
    def test_openrouter(self) -> Dict:
        """تست OpenRouter"""
        api_key = os.getenv('OPENROUTER_API_KEY')
        model = os.getenv('OPENROUTER_MODEL', 'openai/gpt-4')
        
        if not api_key:
            return {
                'provider': 'openrouter',
                'success': False,
                'error': 'OPENROUTER_API_KEY environment variable is required',
                'api_key': None
            }
        
        return self.test_provider('openrouter', api_key=api_key, model=model)
    
    def test_huggingface(self) -> Dict:
        """تست Hugging Face"""
        model_id = os.getenv('HUGGINGFACE_MODEL_ID', 'mistralai/Mistral-7B-Instruct-v0.2')
        api_key = os.getenv('HUGGINGFACE_API_KEY')
        endpoint = os.getenv('HUGGINGFACE_ENDPOINT')
        
        if not api_key and not endpoint:
            return {
                'provider': 'huggingface',
                'success': False,
                'error': 'HUGGINGFACE_API_KEY or HUGGINGFACE_ENDPOINT environment variable is required',
                'api_key': None
            }
        
        return self.test_provider('huggingface', model_id=model_id, api_key=api_key, endpoint=endpoint)
    
    def test_local(self) -> Dict:
        """تست Local Model (Ollama)"""
        base_url = os.getenv('LOCAL_MODEL_URL', 'http://localhost:11434')
        model = os.getenv('LOCAL_MODEL_NAME', 'llama2')
        
        return self.test_provider('local', base_url=base_url, model=model)
    
    def run_all_tests(self):
        """اجرای تمام تست‌ها"""
        self.print_header("🧪 تست جامع وضعیت مدل‌های LLM")
        
        print(f"📅 تاریخ تست: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💬 پیام تست: {self.test_message}\n")
        
        # لیست تمام تست‌ها
        tests = [
            ("OpenAI", self.test_openai),
            ("Anthropic (Claude)", self.test_anthropic),
            ("Google Gemini", self.test_google_gemini),
            ("OpenRouter", self.test_openrouter),
            ("Hugging Face", self.test_huggingface),
            ("Local (Ollama)", self.test_local),
        ]
        
        # اجرای تست‌ها
        for name, test_func in tests:
            try:
                result = test_func()
                self.results.append(result)
            except Exception as e:
                self.print_error(f"خطا در تست {name}: {str(e)}")
                self.results.append({
                    'provider': name.lower(),
                    'success': False,
                    'error': str(e)
                })
        
        # نمایش خلاصه نتایج
        self.print_summary()
    
    def print_summary(self):
        """چاپ خلاصه نتایج"""
        self.print_header("📊 خلاصه نتایج")
        
        successful = [r for r in self.results if r.get('success')]
        failed = [r for r in self.results if not r.get('success')]
        skipped = [r for r in self.results if r.get('error') and 'required' in r.get('error', '').lower()]
        
        print(f"\n{Colors.BOLD}آمار کلی:{Colors.RESET}")
        print(f"  ✅ موفق: {Colors.GREEN}{len(successful)}{Colors.RESET}")
        print(f"  ❌ ناموفق: {Colors.RED}{len(failed) - len(skipped)}{Colors.RESET}")
        print(f"  ⏭️  رد شده (بدون API key): {Colors.YELLOW}{len(skipped)}{Colors.RESET}")
        print(f"  📊 کل: {len(self.results)}\n")
        
        # نمایش نتایج موفق
        if successful:
            print(f"\n{Colors.BOLD}{Colors.GREEN}✅ مدل‌های فعال:{Colors.RESET}")
            for result in successful:
                print(f"  • {result['model_name'] or result['provider']}")
                if result.get('test_time'):
                    print(f"    ⏱️  زمان تست: {result['test_time']:.2f} ثانیه")
                if result.get('response'):
                    response_preview = result['response'][:50] + "..." if len(result['response']) > 50 else result['response']
                    print(f"    📝 پاسخ: {response_preview}")
        
        # نمایش نتایج ناموفق (غیر از رد شده‌ها)
        failed_not_skipped = [r for r in failed if r not in skipped]
        if failed_not_skipped:
            print(f"\n{Colors.BOLD}{Colors.RED}❌ مدل‌های با مشکل:{Colors.RESET}")
            for result in failed_not_skipped:
                print(f"  • {result['provider']}")
                if result.get('error'):
                    error_preview = result['error'][:100] + "..." if len(result['error']) > 100 else result['error']
                    print(f"    ⚠️  خطا: {error_preview}")
        
        # نمایش رد شده‌ها
        if skipped:
            print(f"\n{Colors.BOLD}{Colors.YELLOW}⏭️  مدل‌های رد شده (بدون API key):{Colors.RESET}")
            for result in skipped:
                print(f"  • {result['provider']}")
                if result.get('error'):
                    print(f"    ℹ️  {result['error']}")
        
        # پیشنهادات
        print(f"\n{Colors.BOLD}{Colors.CYAN}💡 پیشنهادات:{Colors.RESET}")
        if not successful:
            print("  • هیچ مدلی فعال نیست. لطفاً حداقل یک API key را در فایل .env تنظیم کنید.")
        elif len(successful) == 1:
            print(f"  • فقط یک مدل فعال است: {successful[0]['model_name']}")
            print("  • می‌توانید مدل‌های دیگر را نیز فعال کنید.")
        else:
            print(f"  • {len(successful)} مدل فعال است. می‌توانید از هر کدام استفاده کنید.")
        
        if skipped:
            print("  • برای فعال کردن مدل‌های رد شده، API key مربوطه را در فایل .env اضافه کنید.")
        
        print()


def main():
    """تابع اصلی"""
    tester = LLMTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  تست توسط کاربر متوقف شد.{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ خطای غیرمنتظره: {str(e)}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # خروج با کد مناسب
    successful_count = len([r for r in tester.results if r.get('success')])
    if successful_count > 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()


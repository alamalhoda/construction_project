"""
AI Agent اصلی برای دستیار هوشمند
استفاده از LangChain Agent با پشتیبانی از چندین LLM provider
"""

import logging
import inspect
import time
from typing import Optional, Dict, Any, Callable
from django.conf import settings
from django.core.cache import cache
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.tools import BaseTool, StructuredTool
from assistant.llm_providers import LLMProviderFactory
from assistant.tools import (
    create_expense,
    get_expense,
    list_expenses,
    get_investor_info,
    list_periods,
    get_expense_stats,
    get_investor_stats,
    get_unit_stats,
    get_period_stats,
    search_expenses
)
# Import تمام ابزارهای تولید شده از schema
from assistant.generated import generated_tools_from_schema
from construction.project_manager import ProjectManager

logger = logging.getLogger(__name__)


class ConstructionAssistantAgent:
    """Agent اصلی برای دستیار هوشمند پروژه ساخت‌وساز"""
    
    def __init__(self, provider_type: Optional[str] = None, request=None, use_rag: bool = True):
        """
        Args:
            provider_type: نوع LLM provider ('openai', 'anthropic', 'huggingface', 'local')
            request: درخواست HTTP برای دریافت پروژه جاری
            use_rag: استفاده از RAG برای دسترسی به مستندات
        """
        self.request = request
        self.use_rag = use_rag
        self.rag_pipeline = None
        
        # ایجاد LLM provider
        if provider_type:
            from django.conf import settings
            import os
            provider_config = getattr(settings, 'AI_ASSISTANT_PROVIDER_CONFIG', {})
            print(f"🔧 Provider: {provider_type}")
            
            # اگر api_key در config وجود ندارد یا None است، از متغیر محیطی استفاده می‌کنیم
            if provider_type.lower() == 'openai' and (not provider_config.get('api_key')):
                env_api_key = os.getenv('OPENAI_API_KEY')
                provider_config['api_key'] = env_api_key
            elif provider_type.lower() == 'openai':
                # اگر api_key در config وجود دارد اما None است، از متغیر محیطی استفاده می‌کنیم
                if not provider_config.get('api_key'):
                    env_api_key = os.getenv('OPENAI_API_KEY')
                    provider_config['api_key'] = env_api_key
            elif provider_type.lower() == 'openrouter':
                # برای OpenRouter هم همین کار را می‌کنیم
                if not provider_config.get('api_key'):
                    env_api_key = os.getenv('OPENROUTER_API_KEY')
                    provider_config['api_key'] = env_api_key
                if not provider_config.get('model'):
                    env_model = os.getenv('OPENROUTER_MODEL', 'google/gemini-2.0-flash-exp:free')
                    provider_config['model'] = env_model
            elif provider_type.lower() == 'gemini' or provider_type.lower() == 'google':
                # برای Google Gemini هم همین کار را می‌کنیم
                if not provider_config.get('api_key'):
                    env_api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
                    provider_config['api_key'] = env_api_key
                if not provider_config.get('model'):
                    env_model = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
                    # پاک کردن کامنت‌ها از نام مدل (اگر وجود داشته باشد)
                    if env_model:
                        env_model = str(env_model).split('#')[0].strip()
                    provider_config['model'] = env_model
                else:
                    # پاک کردن کامنت‌ها از نام مدل موجود در config
                    model_value = provider_config.get('model')
                    if model_value:
                        cleaned_model = str(model_value).split('#')[0].strip()
                        provider_config['model'] = cleaned_model
            
            if provider_config.get('model'):
                print(f"🔧 Model: {provider_config.get('model')}")
            self.provider = LLMProviderFactory.create_provider(provider_type, **provider_config)
        else:
            self.provider = LLMProviderFactory.get_default_provider()
        
        # ایجاد LLM
        self.llm = self.provider.get_llm(temperature=0)
        
        # ایجاد Tools
        self.tools = self._create_tools()
        
        # ایجاد Agent
        self.agent_graph = self._create_agent()
        
        # بارگذاری RAG در صورت نیاز
        if self.use_rag:
            print("⚠️  RAG is enabled. This may try to use OpenAI embeddings.")
            try:
                from assistant.rag import get_rag_pipeline
                self.rag_pipeline = get_rag_pipeline()
                # بررسی اینکه آیا retriever در دسترس است
                if self.rag_pipeline:
                    retriever = self.rag_pipeline.get_retriever()
                    if not retriever:
                        print("Warning: RAG retriever not available. RAG will be disabled.")
                        print("   To enable RAG:")
                        print("   - Install: pip install sentence-transformers torch")
                        print("   - Or set OPENAI_API_KEY environment variable")
                        self.use_rag = False
            except Exception as e:
                print(f"Warning: Could not initialize RAG pipeline: {str(e)}")
                print("   RAG will be disabled.")
                self.use_rag = False
    
    def _create_tools(self):
        """ایجاد لیست Tools برای Agent"""
        request = self.request
        tools_list = []
        
        # Helper function برای ایجاد wrapper با request
        def create_wrapper_with_request(original_func: Callable) -> Callable:
            """ایجاد wrapper function که request را به تابع اصلی اضافه می‌کند و signature را حفظ می‌کند"""
            from functools import wraps
            import inspect
            
            sig = inspect.signature(original_func)
            
            # بررسی اینکه آیا تابع request parameter دارد یا نه
            has_request_param = 'request' in sig.parameters
            
            # ایجاد signature جدید بدون request برای LangChain
            if has_request_param:
                params = list(sig.parameters.values())
                params_without_request = [p for p in params if p.name != 'request']
                new_sig = sig.replace(parameters=params_without_request)
            else:
                new_sig = sig
            
            # ایجاد wrapper function با signature جدید
            def wrapper(*args, **kwargs):
                # اگر request parameter وجود دارد، آن را اضافه کن
                if has_request_param:
                    kwargs['request'] = request
                # فراخوانی تابع اصلی
                return original_func(*args, **kwargs)
            
            # تنظیم signature برای LangChain (بدون request)
            wrapper.__signature__ = new_sig
            wrapper.__name__ = original_func.__name__
            wrapper.__doc__ = original_func.__doc__
            wrapper.__annotations__ = {k: v for k, v in original_func.__annotations__.items() if k != 'request'}
            
            return wrapper
        
        # اضافه کردن ابزارهای قدیمی (برای سازگاری)
        def create_expense_wrapper(amount: float, period_id: int, expense_type: str, description: str = "") -> str:
            """ایجاد یک هزینه جدید"""
            return create_expense.func(amount, period_id, expense_type, description, request)
        
        def get_expense_wrapper(expense_id: int) -> str:
            """دریافت اطلاعات یک هزینه"""
            return get_expense.func(expense_id)
        
        def list_expenses_wrapper(period_id: int = None, expense_type: str = None, limit: int = 20) -> str:
            """لیست هزینه‌ها با فیلتر"""
            return list_expenses.func(period_id, expense_type, limit, request)
        
        def get_investor_info_wrapper(investor_id: int) -> str:
            """دریافت اطلاعات یک سرمایه‌گذار"""
            return get_investor_info.func(investor_id)
        
        def list_periods_wrapper(project_id: int = None) -> str:
            """دریافت لیست دوره‌های پروژه"""
            return list_periods.func(project_id, request)
        
        def get_expense_stats_wrapper(project_id: int = None) -> str:
            """دریافت آمار هزینه‌های پروژه"""
            return get_expense_stats.func(project_id, request)
        
        def get_investor_stats_wrapper(project_id: int = None) -> str:
            """دریافت آمار سرمایه‌گذاران پروژه"""
            return get_investor_stats.func(project_id, request)
        
        def get_unit_stats_wrapper(project_id: int = None) -> str:
            """دریافت آمار واحدهای پروژه"""
            return get_unit_stats.func(project_id, request)
        
        def get_period_stats_wrapper(project_id: int = None) -> str:
            """دریافت آمار دوره‌های پروژه"""
            return get_period_stats.func(project_id, request)
        
        def search_expenses_wrapper(query: str, limit: int = 10) -> str:
            """جستجوی هزینه‌ها بر اساس توضیحات"""
            return search_expenses.func(query, limit, request)
        
        # اضافه کردن ابزارهای قدیمی
        tools_list.extend([
            tool(create_expense_wrapper),
            tool(get_expense_wrapper),
            tool(list_expenses_wrapper),
            tool(get_investor_info_wrapper),
            tool(list_periods_wrapper),
            tool(get_expense_stats_wrapper),
            tool(get_investor_stats_wrapper),
            tool(get_unit_stats_wrapper),
            tool(get_period_stats_wrapper),
            tool(search_expenses_wrapper)
        ])
        
        # اضافه کردن تمام ابزارهای تولید شده از schema
        # استخراج تمام Tool objects از generated_tools_from_schema
        tool_prefixes = [
            'expense_', 'investor_', 'period_', 'project_', 'transaction_',
            'unit_', 'pettycashtransaction_', 'interestrate_', 'sale_',
            'unitspecificexpense_', 'auth_', 'comprehensive_', 'status_'
        ]
        
        for name, obj in inspect.getmembers(generated_tools_from_schema):
            # بررسی اینکه آیا Tool object است و با یکی از prefix ها شروع می‌شود
            if isinstance(obj, BaseTool) and any(name.startswith(prefix) for prefix in tool_prefixes):
                try:
                    # Tool objects قبلاً آماده هستند و request parameter را دارند
                    # اما باید request را به صورت dynamic اضافه کنیم
                    # بهترین راه این است که wrapper function بسازیم
                    if hasattr(obj, 'func'):
                        original_func = obj.func
                        # ایجاد wrapper function که request را اضافه می‌کند
                        wrapped_func = create_wrapper_with_request(original_func)
                        # ایجاد tool جدید با wrapper function
                        # حفظ نام و توضیحات از tool اصلی
                        tool_name = obj.name if hasattr(obj, 'name') else name
                        tool_description = obj.description if hasattr(obj, 'description') else (original_func.__doc__ or '')
                        # استفاده از StructuredTool برای تعیین name و description
                        tool_obj = StructuredTool.from_function(
                            func=wrapped_func,
                            name=tool_name,
                            description=tool_description
                        )
                    else:
                        # اگر func نداریم، از tool اصلی استفاده کنیم
                        tool_obj = obj
                    
                    tools_list.append(tool_obj)
                    logger.debug(f"✅ ابزار اضافه شد: {name}")
                except Exception as e:
                    logger.warning(f"⚠️ خطا در اضافه کردن ابزار {name}: {str(e)}")
                    import traceback
                    logger.warning(traceback.format_exc())
                    continue
        
        logger.info(f"📊 تعداد کل ابزارها: {len(tools_list)}")
        return tools_list
    
    def _create_agent(self):
        """ایجاد Agent executor با استفاده از API جدید langchain 1.0"""
        # دریافت پروژه جاری
        current_project = None
        if self.request:
            current_project = ProjectManager.get_current_project(self.request)
        
        project_name = current_project.name if current_project else "نامشخص"
        
        # ایجاد System Prompt
        system_prompt = f"""شما یک دستیار هوشمند برای سیستم مدیریت پروژه ساخت‌وساز هستید.

پروژه جاری: {project_name}

شما به بیش از 100 ابزار دسترسی دارید که شامل موارد زیر هستند:

📊 **ابزارهای مدیریت هزینه‌ها (Expense):**
- expense_list: دریافت لیست هزینه‌ها
- expense_create: ایجاد هزینه جدید
- expense_retrieve: دریافت اطلاعات یک هزینه
- expense_update: به‌روزرسانی هزینه
- expense_destroy: حذف هزینه
- expense_dashboard_data_retrieve: دریافت داده‌های داشبورد هزینه‌ها
- expense_total_expenses_retrieve: دریافت مجموع هزینه‌ها
- expense_update_expense_create: به‌روزرسانی یا ایجاد هزینه برای دوره و نوع خاص

👥 **ابزارهای مدیریت سرمایه‌گذاران (Investor):**
- investor_list: دریافت لیست سرمایه‌گذاران
- investor_create: ایجاد سرمایه‌گذار جدید
- investor_retrieve: دریافت اطلاعات یک سرمایه‌گذار
- investor_detailed_statistics_retrieve: دریافت آمار تفصیلی سرمایه‌گذار
- investor_ownership_retrieve: دریافت اطلاعات مالکیت
- investor_summary_retrieve: دریافت خلاصه سرمایه‌گذاران

📅 **ابزارهای مدیریت دوره‌ها (Period):**
- period_list: دریافت لیست دوره‌ها
- period_create: ایجاد دوره جدید
- period_retrieve: دریافت اطلاعات یک دوره
- period_chart_data_retrieve: دریافت داده‌های نمودار دوره‌ها
- period_period_summary_retrieve: دریافت خلاصه دوره‌ها

🏢 **ابزارهای مدیریت پروژه‌ها (Project):**
- project_list: دریافت لیست پروژه‌ها
- project_create: ایجاد پروژه جدید
- project_retrieve: دریافت اطلاعات یک پروژه
- project_active_retrieve: دریافت پروژه فعال
- project_statistics_retrieve: دریافت آمار پروژه
- project_comprehensive_analysis_retrieve: دریافت تحلیل جامع پروژه

💰 **ابزارهای مدیریت تراکنش‌ها (Transaction):**
- transaction_list: دریافت لیست تراکنش‌ها
- transaction_create: ایجاد تراکنش جدید
- transaction_retrieve: دریافت اطلاعات یک تراکنش
- transaction_statistics_retrieve: دریافت آمار تراکنش‌ها
- transaction_detailed_statistics_retrieve: دریافت آمار تفصیلی تراکنش‌ها

🏠 **ابزارهای مدیریت واحدها (Unit):**
- unit_list: دریافت لیست واحدها
- unit_create: ایجاد واحد جدید
- unit_retrieve(id: int): دریافت اطلاعات یک واحد خاص - **⚠️ نیاز به id دارد (عدد صحیح)**
- unit_statistics_retrieve: دریافت آمار واحدها

**مثال استفاده از unit_retrieve:**
- سوال کاربر: "اطلاعات کامل واحد شماره ۱ را بده"
- شما باید: 
  1. ابتدا عدد 1 را از سوال استخراج کنید
  2. سپس unit_retrieve(id=1) را فراخوانی کنید
  3. برای دریافت اطلاعات مالکین، از investor_list استفاده کنید
  4. **نحوه پیدا کردن مالکین:**
     * پاسخ investor_list یک آرایه JSON است که هر عنصر آن یک سرمایه‌گذار است
     * برای هر سرمایه‌گذار در این آرایه:
       - فیلد "units" را بررسی کنید (یک آرایه از واحدها)
       - در این آرایه، به دنبال واحدی بگردید که `id` آن برابر با 1 باشد
       - اگر پیدا کردید، این سرمایه‌گذار مالک واحد شماره 1 است
     * مثال: اگر investor.units یک آرایه شامل واحد با id=1 باشد، این سرمایه‌گذار مالک واحد 1 است
- **هیچ‌وقت unit_retrieve() را بدون id فراخوانی نکنید**
- **مهم:** unit_retrieve فقط اطلاعات پایه واحد را برمی‌گرداند. برای اطلاعات مالکین، باید از investor_list استفاده کنید و در فیلد `units` هر سرمایه‌گذار جستجو کنید

💵 **ابزارهای مدیریت صندوق خرد (PettyCash):**
- pettycashtransaction_list: دریافت لیست تراکنش‌های صندوق خرد
- pettycashtransaction_create: ایجاد تراکنش صندوق خرد
- pettycashtransaction_balance_detail_retrieve: دریافت جزئیات موجودی صندوق خرد
- pettycashtransaction_balances_retrieve: دریافت موجودی‌های صندوق خرد

📈 **ابزارهای مدیریت نرخ سود (InterestRate):**
- interestrate_list: دریافت لیست نرخ‌های سود
- interestrate_create: ایجاد نرخ سود جدید
- interestrate_current_retrieve: دریافت نرخ سود فعلی

💼 **ابزارهای مدیریت فروش (Sale):**
- sale_list: دریافت لیست فروش‌ها
- sale_create: ایجاد فروش جدید
- sale_total_sales_retrieve: دریافت مجموع فروش‌ها

🔐 **ابزارهای احراز هویت (Auth):**
- auth_login_create: ورود به سیستم
- auth_logout_create: خروج از سیستم
- auth_user_retrieve: دریافت اطلاعات کاربر
- auth_register_create: ثبت نام کاربر جدید

**قوانین مهم:**
1. همیشه ابتدا از tools استفاده کنید و سپس پاسخ دهید
2. برای ابزارهایی که project_id اختیاری است، اگر داده نشود، از پروژه جاری استفاده می‌شود
3. تمام ابزارها به صورت خودکار request را دریافت می‌کنند و نیازی به ارسال آن نیست

4. **⚠️ قانون طلایی برای ابزارهای retrieve (unit_retrieve, investor_retrieve, expense_retrieve, period_retrieve, transaction_retrieve):**
   - **این ابزارها همیشه نیاز به پارامتر id دارند که باید یک عدد صحیح (int) باشد**
   - **هیچ‌وقت ابزار retrieve را بدون id فراخوانی نکنید - این کار باعث خطا می‌شود**
   - **مراحل استفاده:**
     * ابتدا از سوال کاربر عدد id را استخراج کنید
     * سپس ابزار را با id استخراج شده فراخوانی کنید
   - **مثال‌های صحیح:**
     * سوال: "اطلاعات واحد شماره 1" → استخراج id=1 → unit_retrieve(id=1)
     * سوال: "واحد 5" → استخراج id=5 → unit_retrieve(id=5)
     * سوال: "سرمایه‌گذار شماره 10" → استخراج id=10 → investor_retrieve(id=10)
     * سوال: "هزینه 20" → استخراج id=20 → expense_retrieve(id=20)
   - **مثال‌های نادرست (هرگز این کار را نکنید):**
     * unit_retrieve() ❌ (بدون id - خطا می‌دهد)
     * unit_retrieve(id="1") ❌ (id باید int باشد، نه string)
     * unit_retrieve(id=None) ❌ (id نمی‌تواند None باشد)
   - **اگر id را از سوال کاربر پیدا نکردید:**
     * ابتدا از ابزار list استفاده کنید (مثلاً unit_list) تا لیست را ببینید
     * سپس از کاربر بپرسید یا از اطلاعات list استفاده کنید

5. **برای سوالات پیچیده که نیاز به اطلاعات چندگانه دارند، از چند ابزار استفاده کنید و نتایج را با هم ترکیب کنید:**
   - **⚠️ قانون مهم: برای سوالات درباره واحدها، همیشه مالکین را هم پیدا کنید:**
     * وقتی کاربر سوالی درباره یک واحد می‌پرسد (مثلاً "اطلاعات کامل واحد شماره X")، باید:
       1. ابتدا unit_retrieve(id=X) را فراخوانی کنید
       2. سپس investor_list را فراخوانی کنید
       3. **نحوه جستجو در فیلد units:**
          - پاسخ investor_list یک آرایه JSON است
          - هر سرمایه‌گذار یک فیلد `units` دارد که یک آرایه از واحدها است
          - برای پیدا کردن مالکین واحد شماره X:
            * برای هر سرمایه‌گذار در لیست:
              - فیلد `units` را بررسی کنید (یک آرایه JSON)
              - در این آرایه، به دنبال واحدی بگردید که فیلد `id` آن برابر با X باشد
              - اگر پیدا کردید، این سرمایه‌گذار مالک واحد شماره X است
          - مثال: اگر واحدی با `id=1` در `units` سرمایه‌گذار با `id=11` وجود دارد، پس سرمایه‌گذار 11 مالک واحد 1 است
       4. اطلاعات تمام مالکین پیدا شده را به پاسخ اضافه کنید
     * اگر واحدی مالک نداشت، آن را به عنوان "بدون مالک" یا "خالی" نمایش دهید
     * **مهم:** حتماً در آرایه `units` هر سرمایه‌گذار جستجو کنید و فیلد `id` واحدها را با id واحد مورد نظر مقایسه کنید
   - **مثال: سوال درباره واحدها و مالکین:**
     * ابتدا از `unit_list` لیست کامل همه واحدها را بگیرید
     * سپس از `investor_list` لیست سرمایه‌گذاران و واحدهایشان را بگیرید
     * **مهم - نحوه تطبیق:**
       - پاسخ investor_list یک آرایه JSON است که هر عنصر آن یک سرمایه‌گذار است
       - هر سرمایه‌گذار یک فیلد "units" دارد که یک آرایه از واحدها است
       - برای پیدا کردن مالکین واحد با id=X:
         * برای هر سرمایه‌گذار در لیست:
           - فیلد `units` را بررسی کنید (یک آرایه)
           - در این آرایه، به دنبال واحدی بگردید که `id` آن برابر با X باشد
           - اگر پیدا کردید، این سرمایه‌گذار مالک است
       - مثال: اگر investor.units یک آرایه شامل واحد با id=X باشد، این سرمایه‌گذار مالک واحد X است
     * برای هر واحد، مالک(ین) آن را از لیست سرمایه‌گذاران پیدا کنید
     * اگر واحدی مالک نداشت، آن را به عنوان "خالی" یا "-" نمایش دهید
   - **مثال: سوال درباره پروژه و هزینه‌ها:**
     * از project_list و expense_list استفاده کنید و نتایج را با هم ترکیب کنید
   - **مثال: سوال درباره تراکنش‌ها و سرمایه‌گذاران:**
     * از transaction_list و investor_list استفاده کنید و تراکنش‌ها را با سرمایه‌گذاران تطبیق دهید
   - **همیشه:** برای سوالات ترکیبی، ابتدا همه داده‌های لازم را جمع‌آوری کنید، سپس آن‌ها را با هم ترکیب و تحلیل کنید
6. **مثال‌های عملی استفاده از tools:**

   **مثال 1: سوال درباره یک واحد خاص (شامل مالکین)**
   - سوال: "اطلاعات کامل واحد شماره ۱ را بده"
   - مراحل:
     1. استخراج id از سوال: id = 1
     2. فراخوانی: unit_retrieve(id=1) برای دریافت اطلاعات پایه واحد
     3. فراخوانی: investor_list برای دریافت لیست سرمایه‌گذاران و واحدهایشان
     4. پیدا کردن مالکین: در لیست سرمایه‌گذاران، سرمایه‌گذارانی که در فیلد `units` آن‌ها واحدی با `id=1` وجود دارد
     5. نمایش اطلاعات واحد + اطلاعات مالکین
   
   **مثال 2: سوال درباره یک سرمایه‌گذار**
   - سوال: "سرمایه‌گذار 5 چه کسی است؟"
   - مراحل:
     1. استخراج id از سوال: id = 5
     2. فراخوانی: investor_retrieve(id=5)
     3. نمایش اطلاعات سرمایه‌گذار
   
   **مثال 3: سوال بدون id مشخص**
   - سوال: "لیست واحدها را بده"
   - مراحل:
     1. چون id مشخص نیست، از unit_list استفاده کنید
     2. نمایش لیست کامل واحدها
   
   **مثال 4: سوال درباره مالکین یک واحد**
   - سوال: "واحد شماره 1 چه کسی مالک آن است؟" یا "اطلاعات کامل واحد شماره 1 را بده" (شامل مالکین)
   - مراحل:
     1. ابتدا unit_retrieve(id=1) برای دریافت اطلاعات پایه واحد
     2. سپس investor_list برای دریافت لیست کامل سرمایه‌گذاران (که شامل units هر سرمایه‌گذار است)
     3. **مهم - نحوه جستجو در فیلد units:**
        * پاسخ investor_list یک آرایه JSON از سرمایه‌گذاران است
        * هر سرمایه‌گذار یک فیلد `units` دارد که یک آرایه از واحدها است
        * برای پیدا کردن مالکین واحد شماره 1:
          - برای هر سرمایه‌گذار در لیست:
            - فیلد `units` را بررسی کنید (یک آرایه است)
            - در این آرایه، به دنبال واحدی بگردید که `id` آن برابر با 1 باشد
            - اگر پیدا کردید، این سرمایه‌گذار مالک واحد شماره 1 است
        * مثال ساختار JSON:
          پاسخ investor_list یک آرایه است که هر عنصر آن یک سرمایه‌گذار است
          هر سرمایه‌گذار یک فیلد "units" دارد که یک آرایه از واحدها است
          هر واحد در این آرایه یک فیلد "id" دارد
          برای پیدا کردن مالکین واحد شماره 1، باید در فیلد "units" هر سرمایه‌گذار، واحدی با "id" برابر با 1 را پیدا کنید
        * در این مثال، اگر سرمایه‌گذار با id=11 در فیلد "units" خود واحدی با id=1 داشته باشد، این سرمایه‌گذار مالک واحد شماره 1 است
     4. اطلاعات تمام مالکین پیدا شده را به پاسخ اضافه کنید
   
   **نکته مهم درباره رابطه واحد و مالک:**
   - رابطه بین Unit و Investor یک رابطه ManyToMany است
   - هر سرمایه‌گذار می‌تواند چندین واحد داشته باشد (در فیلد `units` که یک آرایه است)
   - هر واحد می‌تواند چندین مالک داشته باشد
   - برای پیدا کردن مالکین یک واحد با id=X:
     * از `investor_list` استفاده کنید
     * برای هر سرمایه‌گذار، فیلد `units` را بررسی کنید (یک آرایه JSON)
     * در این آرایه، به دنبال واحدی با `id == X` بگردید
     * اگر پیدا کردید، این سرمایه‌گذار مالک است
   - اگر واحدی مالک نداشت، آن را به عنوان "بدون مالک" یا "خالی" نمایش دهید

7. همیشه پاسخ‌های خود را به فارسی و به صورت دوستانه و مفید بدهید
8. اگر کاربر سوالی درباره API یا مستندات پرسید، از اطلاعات RAG استفاده کنید

**انواع هزینه‌ها:**
- مدیر پروژه (project_manager)
- سرپرست کارگاه (facilities_manager)
- کارپرداز (procurement)
- انباردار (warehouse)
- پیمان ساختمان (construction_contractor)
- سایر (other)

**انواع تراکنش‌ها:**
- آورده (principal_deposit)
- برداشت (principal_withdrawal)
- سود مشارکت (profit)
- خروجی (withdrawal)
"""
        
        # استفاده از API جدید create_agent
        # این API یک StateGraph برمی‌گرداند که می‌تواند مستقیماً invoke شود
        agent_graph = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt,
            debug=False
        )
        
        return agent_graph
    
    def _check_rate_limit(self, user_id: Optional[str] = None) -> bool:
        """
        بررسی rate limit برای کاربر
        
        Args:
            user_id: شناسه کاربر (اختیاری)
        
        Returns:
            True اگر درخواست مجاز است، False در غیر این صورت
        """
        # استفاده از IP یا user_id برای rate limiting
        if self.request:
            identifier = f"rate_limit_{self.request.user.id if self.request.user.is_authenticated else self.request.META.get('REMOTE_ADDR', 'anonymous')}"
        else:
            identifier = f"rate_limit_{user_id or 'anonymous'}"
        
        # محدودیت: حداکثر 30 درخواست در دقیقه
        max_requests = 30
        period = 60  # 60 ثانیه
        
        cache_key = f"agent_rate_limit_{identifier}"
        current_time = time.time()
        
        # دریافت اطلاعات rate limit از cache
        rate_limit_data = cache.get(cache_key, {'requests': [], 'last_reset': current_time})
        
        # پاک کردن درخواست‌های قدیمی‌تر از period
        rate_limit_data['requests'] = [
            req_time for req_time in rate_limit_data['requests']
            if current_time - req_time < period
        ]
        
        # بررسی اینکه آیا به حد مجاز رسیده‌ایم یا نه
        if len(rate_limit_data['requests']) >= max_requests:
            return False
        
        # اضافه کردن درخواست فعلی
        rate_limit_data['requests'].append(current_time)
        cache.set(cache_key, rate_limit_data, period + 10)  # ذخیره برای مدت بیشتر
        
        return True
    
    def invoke(self, message: str, chat_history: list = None) -> Dict[str, Any]:
        """
        اجرای Agent با پیام کاربر و تاریخچه چت
        
        Args:
            message: پیام کاربر
            chat_history: لیست تاریخچه چت (اختیاری) - فرمت: [{'role': 'user'|'assistant', 'content': '...'}, ...]
        
        Returns:
            نتیجه اجرای Agent
        """
        # بررسی rate limit
        if not self._check_rate_limit():
            error_message = (
                "⚠️ محدودیت نرخ درخواست: شما درخواست‌های زیادی ارسال کرده‌اید. "
                "لطفاً یک دقیقه صبر کنید و دوباره تلاش کنید."
            )
            logger.warning("⚠️ Rate limit exceeded for user")
            return {
                "output": error_message,
                "success": False,
                "error": "Rate limit exceeded"
            }
        
        try:
            # تبدیل تاریخچه به فرمت LangChain messages
            from langchain_core.messages import HumanMessage, AIMessage
            
            messages = []
            
            # اگر تاریخچه وجود دارد، آن را اضافه کن
            if chat_history:
                for item in chat_history:
                    if item.get('role') == 'user':
                        messages.append(HumanMessage(content=item.get('content', '')))
                    elif item.get('role') == 'assistant':
                        messages.append(AIMessage(content=item.get('content', '')))
            
            # اگر RAG فعال است و سوال درباره API است، از RAG استفاده کن
            if self.use_rag and self.rag_pipeline:
                # بررسی اینکه آیا سوال درباره API است
                api_keywords = ['api', 'endpoint', 'مستندات', 'documentation', 'چطور', 'چگونه']
                if any(keyword in message.lower() for keyword in api_keywords):
                    # جستجو در مستندات
                    relevant_docs = self.rag_pipeline.search(message)
                    if relevant_docs:
                        # اضافه کردن اطلاعات RAG به پیام
                        rag_context = "\n\nاطلاعات مرتبط از مستندات:\n"
                        for doc in relevant_docs[:2]:  # فقط 2 نتیجه اول
                            rag_context += f"- {doc.page_content[:200]}...\n"
                        message = message + rag_context
            
            # اضافه کردن پیام فعلی کاربر
            messages.append(HumanMessage(content=message))
            
            # دریافت پروژه جاری
            current_project = None
            if self.request:
                current_project = ProjectManager.get_current_project(self.request)
            
            project_name = current_project.name if current_project else "نامشخص"
            
            # اجرای Agent با API جدید
            # در langchain 1.0، agent_graph یک StateGraph است که با messages invoke می‌شود
            
            logger.info("🔄 در حال پردازش درخواست...")
            if chat_history:
                logger.info(f"📜 تاریخچه چت: {len(chat_history)} پیام قبلی")
                print(f"📜 تاریخچه چت: {len(chat_history)} پیام قبلی")
            print("🔄 در حال پردازش درخواست...")
            
            # استفاده از messages به جای فقط یک HumanMessage
            # با retry logic برای مدیریت rate limit
            max_retries = 5
            base_delay = 2  # شروع با 2 ثانیه
            result = None
            
            for attempt in range(max_retries):
                try:
                    result = self.agent_graph.invoke({
                        "messages": messages
                    })
                    break  # موفق بود، از حلقه خارج شو
                except Exception as e:
                    error_str = str(e)
                    
                    # بررسی اینکه آیا خطای rate limit است
                    is_rate_limit = (
                        "429" in error_str or 
                        "ResourceExhausted" in error_str or 
                        "rate limit" in error_str.lower()
                    )
                    
                    if is_rate_limit and attempt < max_retries - 1:
                        # محاسبه delay با exponential backoff
                        delay = base_delay * (2 ** attempt)  # 2, 4, 8, 16, 32 ثانیه
                        # محدود کردن delay به حداکثر 60 ثانیه
                        delay = min(delay, 60)
                        
                        logger.warning(
                            f"⚠️ Rate limit error (attempt {attempt + 1}/{max_retries}). "
                            f"Waiting {delay} seconds before retry..."
                        )
                        print(
                            f"⚠️ محدودیت نرخ درخواست از سمت Google Gemini (تلاش {attempt + 1}/{max_retries}). "
                            f"در حال انتظار {delay} ثانیه..."
                        )
                        
                        # انتظار قبل از retry
                        time.sleep(delay)
                        continue
                    else:
                        # خطای دیگر یا آخرین تلاش - خطا را throw کن
                        raise
            
            if result is None:
                raise Exception("Failed to get response after all retries")
            
            # لاگ کردن استفاده از tools
            if result.get("messages"):
                tool_usage_count = 0
                tool_calls_seen = set()  # مجموعه tool_call های دیده شده برای جلوگیری از تکرار
                
                for msg in result["messages"]:
                    # فقط tool_calls را شمارش می‌کنیم (ToolMessage ها فقط نتیجه هستند، نه فراخوانی)
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            tool_name = tool_call.get('name', 'نامشخص') if isinstance(tool_call, dict) else getattr(tool_call, 'name', 'نامشخص')
                            tool_id = tool_call.get('id', None) if isinstance(tool_call, dict) else getattr(tool_call, 'id', None)
                            
                            # استفاده از tool_id برای جلوگیری از شمارش تکراری
                            # اگر tool_id نداشت، از tool_name استفاده می‌کنیم
                            unique_key = tool_id if tool_id else f"{tool_name}_{id(tool_call)}"
                            
                            if unique_key not in tool_calls_seen:
                                tool_usage_count += 1
                                tool_calls_seen.add(unique_key)
                                logger.info(f"🔧 استفاده از ابزار: {tool_name}")
                                print(f"🔧 استفاده از ابزار: {tool_name}")
                
                if tool_usage_count > 0:
                    logger.info(f"📊 مجموع ابزارهای استفاده شده: {tool_usage_count}")
                    print(f"📊 مجموع ابزارهای استفاده شده: {tool_usage_count}")
            
            # استخراج پاسخ از نتیجه
            # در API جدید، پاسخ در messages آخرین AI message است
            output = ""
            if result.get("messages"):
                # پیدا کردن آخرین AI message (پاسخ جدید)
                # باید از انتها به ابتدا جستجو کنیم تا آخرین پاسخ را پیدا کنیم
                for msg in reversed(result["messages"]):
                    # بررسی اینکه آیا این یک AIMessage است
                    if isinstance(msg, AIMessage):
                        if hasattr(msg, 'content'):
                            output = msg.content
                            break
                    # یا اینکه یک dict با type='ai' است
                    elif isinstance(msg, dict):
                        if msg.get('type') == 'ai' and 'content' in msg:
                            output = msg.get('content', '')
                            break
                        elif 'content' in msg:
                            # اگر type مشخص نیست اما content دارد، بررسی می‌کنیم
                            # فقط اگر از قبل AIMessage نبوده باشد
                            if not output:
                                output = msg.get('content', '')
                
                # اگر output خالی است، از آخرین message استفاده کن
                if not output:
                    last_message = result["messages"][-1]
                    if hasattr(last_message, 'content'):
                        output = last_message.content
                    elif isinstance(last_message, dict) and 'content' in last_message:
                        output = last_message['content']
            
            # نمایش پاسخ هوش مصنوعی در کنسول
            logger.info("🤖 پاسخ هوش مصنوعی:")
            logger.info(output)
            logger.info("=" * 80)
            print("🤖 پاسخ هوش مصنوعی:")
            print(output)
            print("=" * 80)
            
            return {
                "output": output or "پاسخ دریافت نشد.",
                "success": True
            }
        
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            error_str = str(e)
            
            # تشخیص نوع خطا و نمایش پیام مناسب
            if "429" in error_str or "ResourceExhausted" in error_str or "rate limit" in error_str.lower():
                error_message = "⚠️ محدودیت نرخ درخواست: سرویس Google Gemini در حال حاضر شلوغ است. لطفاً چند لحظه صبر کنید و دوباره تلاش کنید."
                logger.warning("⚠️ Rate Limit Error (429):")
                logger.warning(error_str)
            elif "timeout" in error_str.lower() or "timed out" in error_str.lower():
                error_message = "⏱️ زمان انتظار به پایان رسید. لطفاً دوباره تلاش کنید."
                logger.error("⏱️ Timeout Error:")
                logger.error(error_str)
            elif "401" in error_str or "Unauthorized" in error_str or "Invalid API key" in error_str:
                error_message = "🔑 خطا در احراز هویت: API key نامعتبر است. لطفاً تنظیمات را بررسی کنید."
                logger.error("🔑 Authentication Error:")
                logger.error(error_str)
            else:
                error_message = f"❌ خطا در پردازش درخواست: {error_str}"
                logger.error("❌ خطا در پردازش درخواست:")
                logger.error(error_str)
            
            # نمایش traceback فقط در حالت debug
            if settings.DEBUG:
                logger.error("Traceback:")
                logger.error(error_traceback)
                print("❌ خطا در پردازش درخواست:")
                print(error_str)
                print("Traceback:")
                print(error_traceback)
            else:
                print(f"❌ خطا: {error_str}")
            
            logger.error("=" * 80)
            print("=" * 80)
            
            return {
                "output": error_message,
                "success": False,
                "error": error_str
            }
    
    def chat(self, message: str) -> str:
        """
        متد ساده برای چت (فقط متن پاسخ را برمی‌گرداند)
        
        Args:
            message: پیام کاربر
        
        Returns:
            پاسخ Agent
        """
        result = self.invoke(message)
        return result.get("output", "متأسفانه خطایی رخ داد.")


def create_assistant_agent(request=None, provider_type: Optional[str] = None, use_rag: bool = True) -> ConstructionAssistantAgent:
    """
    Factory function برای ایجاد Agent
    
    Args:
        request: درخواست HTTP
        provider_type: نوع LLM provider
        use_rag: استفاده از RAG
    
    Returns:
        ConstructionAssistantAgent instance
    """
    return ConstructionAssistantAgent(
        provider_type=provider_type,
        request=request,
        use_rag=use_rag
    )


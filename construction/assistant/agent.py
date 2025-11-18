"""
AI Agent اصلی برای دستیار هوشمند
استفاده از LangChain Agent با پشتیبانی از چندین LLM provider
"""

import logging
from typing import Optional, Dict, Any
from langchain.agents import create_agent
from construction.assistant.llm_providers import LLMProviderFactory
from construction.assistant.tools import (
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
            provider_config = getattr(settings, 'AI_ASSISTANT_PROVIDER_CONFIG', {})
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
            try:
                from construction.assistant.rag import get_rag_pipeline
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
        from langchain.tools import tool
        
        # Wrapper functions برای اضافه کردن request
        request = self.request
        
        # تعریف wrapper functions بدون decorator
        # استفاده از underlying function از tools
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
        
        # ایجاد tools از wrapper functions
        create_expense_tool = tool(create_expense_wrapper)
        get_expense_tool = tool(get_expense_wrapper)
        list_expenses_tool = tool(list_expenses_wrapper)
        get_investor_info_tool = tool(get_investor_info_wrapper)
        list_periods_tool = tool(list_periods_wrapper)
        get_expense_stats_tool = tool(get_expense_stats_wrapper)
        get_investor_stats_tool = tool(get_investor_stats_wrapper)
        get_unit_stats_tool = tool(get_unit_stats_wrapper)
        get_period_stats_tool = tool(get_period_stats_wrapper)
        search_expenses_tool = tool(search_expenses_wrapper)
        
        return [
            create_expense_tool,
            get_expense_tool,
            list_expenses_tool,
            get_investor_info_tool,
            list_periods_tool,
            get_expense_stats_tool,
            get_investor_stats_tool,
            get_unit_stats_tool,
            get_period_stats_tool,
            search_expenses_tool
        ]
    
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

شما می‌توانید از ابزارهای زیر استفاده کنید:
- list_periods_tool: برای دریافت لیست دوره‌های پروژه (نیازی به project_id نیست، از پروژه جاری استفاده می‌شود)
- get_expense_stats_tool: برای دریافت آمار هزینه‌های پروژه (نیازی به project_id نیست)
- get_investor_stats_tool: برای دریافت آمار سرمایه‌گذاران پروژه (نیازی به project_id نیست)
- get_unit_stats_tool: برای دریافت آمار واحدهای پروژه (نیازی به project_id نیست)
- get_period_stats_tool: برای دریافت آمار دوره‌های پروژه (نیازی به project_id نیست)
- list_expenses_tool: برای لیست هزینه‌ها
- create_expense_tool: برای ایجاد هزینه جدید
- get_expense_tool: برای دریافت اطلاعات یک هزینه
- search_expenses_tool: برای جستجوی هزینه‌ها
- get_investor_info_tool: برای دریافت اطلاعات سرمایه‌گذار

مهم: برای ابزارهای آمار (get_expense_stats_tool, get_investor_stats_tool, get_unit_stats_tool, get_period_stats_tool) و list_periods_tool، اگر project_id داده نشود، از پروژه جاری استفاده می‌شود.
برای گزارش جامع پروژه، می‌توانید از تمام ابزارهای آمار استفاده کنید و نتایج را جمع‌بندی کنید.
همیشه ابتدا از tools استفاده کنید و سپس پاسخ دهید.

انواع هزینه‌ها:
- مدیر پروژه (project_manager)
- سرپرست کارگاه (facilities_manager)
- کارپرداز (procurement)
- انباردار (warehouse)
- پیمان ساختمان (construction_contractor)
- سایر (other)

همیشه پاسخ‌های خود را به فارسی و به صورت دوستانه و مفید بدهید.
اگر کاربر سوالی درباره API یا مستندات پرسید، از اطلاعات RAG استفاده کنید.
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
    
    def invoke(self, message: str) -> Dict[str, Any]:
        """
        اجرای Agent با پیام کاربر
        
        Args:
            message: پیام کاربر
        
        Returns:
            نتیجه اجرای Agent
        """
        try:
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
            
            # دریافت پروژه جاری
            current_project = None
            if self.request:
                current_project = ProjectManager.get_current_project(self.request)
            
            project_name = current_project.name if current_project else "نامشخص"
            
            # اجرای Agent با API جدید
            # در langchain 1.0، agent_graph یک StateGraph است که با messages invoke می‌شود
            from langchain_core.messages import HumanMessage
            
            logger.info("🔄 در حال پردازش درخواست...")
            print("🔄 در حال پردازش درخواست...")
            
            result = self.agent_graph.invoke({
                "messages": [HumanMessage(content=message)]
            })
            
            # لاگ کردن استفاده از tools
            if result.get("messages"):
                tool_usage_count = 0
                for msg in result["messages"]:
                    # بررسی tool_calls در message
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        tool_usage_count += len(msg.tool_calls)
                        for tool_call in msg.tool_calls:
                            tool_name = tool_call.get('name', 'نامشخص') if isinstance(tool_call, dict) else getattr(tool_call, 'name', 'نامشخص')
                            logger.info(f"🔧 استفاده از ابزار: {tool_name}")
                            print(f"🔧 استفاده از ابزار: {tool_name}")
                    # بررسی ToolMessage
                    elif hasattr(msg, 'name') and hasattr(msg, 'content'):
                        if 'tool' in str(type(msg)).lower() or 'ToolMessage' in str(type(msg)):
                            tool_usage_count += 1
                            tool_name = getattr(msg, 'name', 'نامشخص')
                            logger.info(f"🔧 استفاده از ابزار: {tool_name}")
                            print(f"🔧 استفاده از ابزار: {tool_name}")
                
                if tool_usage_count > 0:
                    logger.info(f"📊 مجموع ابزارهای استفاده شده: {tool_usage_count}")
                    print(f"📊 مجموع ابزارهای استفاده شده: {tool_usage_count}")
            
            # استخراج پاسخ از نتیجه
            # در API جدید، پاسخ در messages آخرین AI message است
            output = ""
            if result.get("messages"):
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
            error_message = f"❌ خطا در پردازش درخواست: {str(e)}"
            # نمایش خطا در کنسول
            logger.error("❌ خطا در پردازش درخواست:")
            logger.error(str(e))
            logger.error("=" * 80)
            print("❌ خطا در پردازش درخواست:")
            print(str(e))
            print("=" * 80)
            return {
                "output": error_message,
                "success": False,
                "error": str(e)
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


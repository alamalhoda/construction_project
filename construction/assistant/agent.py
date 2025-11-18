"""
AI Agent اصلی برای دستیار هوشمند
استفاده از LangChain Agent با پشتیبانی از چندین LLM provider
"""

from typing import Optional, Dict, Any
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from construction.assistant.llm_providers import LLMProviderFactory
from construction.assistant.tools import (
    create_expense,
    get_expense,
    list_expenses,
    get_investor_info,
    list_periods,
    get_project_stats,
    search_expenses
)
from construction.project_manager import ProjectManager


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
        self.agent_executor = self._create_agent()
        
        # بارگذاری RAG در صورت نیاز
        if self.use_rag:
            try:
                from construction.assistant.rag import get_rag_pipeline
                self.rag_pipeline = get_rag_pipeline()
            except Exception as e:
                print(f"Warning: Could not initialize RAG pipeline: {str(e)}")
                self.use_rag = False
    
    def _create_tools(self):
        """ایجاد لیست Tools برای Agent"""
        from langchain.tools import tool
        
        # Wrapper functions برای اضافه کردن request
        request = self.request
        
        @tool
        def create_expense_tool(amount: float, period_id: int, expense_type: str, description: str = "") -> str:
            """ایجاد یک هزینه جدید"""
            return create_expense(amount, period_id, expense_type, description, request)
        
        @tool
        def get_expense_tool(expense_id: int) -> str:
            """دریافت اطلاعات یک هزینه"""
            return get_expense(expense_id)
        
        @tool
        def list_expenses_tool(period_id: int = None, expense_type: str = None, limit: int = 20) -> str:
            """لیست هزینه‌ها با فیلتر"""
            return list_expenses(period_id, expense_type, limit, request)
        
        @tool
        def get_investor_info_tool(investor_id: int) -> str:
            """دریافت اطلاعات یک سرمایه‌گذار"""
            return get_investor_info(investor_id)
        
        @tool
        def list_periods_tool(project_id: int = None) -> str:
            """دریافت لیست دوره‌های پروژه"""
            return list_periods(project_id, request)
        
        @tool
        def get_project_stats_tool(project_id: int = None) -> str:
            """دریافت آمار پروژه"""
            return get_project_stats(project_id, request)
        
        @tool
        def search_expenses_tool(query: str, limit: int = 10) -> str:
            """جستجوی هزینه‌ها بر اساس توضیحات"""
            return search_expenses(query, limit, request)
        
        return [
            create_expense_tool,
            get_expense_tool,
            list_expenses_tool,
            get_investor_info_tool,
            list_periods_tool,
            get_project_stats_tool,
            search_expenses_tool
        ]
    
    def _create_agent(self):
        """ایجاد Agent executor"""
        # دریافت پروژه جاری
        current_project = None
        if self.request:
            current_project = ProjectManager.get_current_project(self.request)
        
        project_name = current_project.name if current_project else "نامشخص"
        
        # ایجاد Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""شما یک دستیار هوشمند برای سیستم مدیریت پروژه ساخت‌وساز هستید.

پروژه جاری: {project_name}

شما می‌توانید:
- ایجاد هزینه‌های جدید
- دریافت اطلاعات هزینه‌ها
- لیست دوره‌ها
- دریافت آمار پروژه
- جستجوی هزینه‌ها

انواع هزینه‌ها:
- مدیر پروژه (project_manager)
- سرپرست کارگاه (facilities_manager)
- کارپرداز (procurement)
- انباردار (warehouse)
- پیمان ساختمان (construction_contractor)
- سایر (other)

همیشه پاسخ‌های خود را به فارسی و به صورت دوستانه و مفید بدهید.
اگر کاربر سوالی درباره API یا مستندات پرسید، از اطلاعات RAG استفاده کنید.
"""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # بررسی پشتیبانی از Function Calling
        if self.provider.supports_function_calling():
            # استفاده از OpenAI Functions Agent
            agent = create_openai_functions_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )
        else:
            # برای providers که از Function Calling پشتیبانی نمی‌کنند
            # باید از Agent دیگری استفاده کنیم
            from langchain.agents import create_react_agent
            from langchain import hub
            
            # استفاده از ReAct Agent
            react_prompt = hub.pull("hwchase17/react")
            agent = create_react_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=react_prompt
            )
        
        # ایجاد Agent Executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
        
        return agent_executor
    
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
            
            # اجرای Agent
            result = self.agent_executor.invoke({
                "input": message,
                "project_name": project_name
            })
            
            return {
                "output": result.get("output", ""),
                "success": True
            }
        
        except Exception as e:
            return {
                "output": f"❌ خطا در پردازش درخواست: {str(e)}",
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


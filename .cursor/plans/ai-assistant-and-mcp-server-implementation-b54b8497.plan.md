<!-- b54b8497-a9f0-48e6-a138-1a31d48a0c0a c0aadcfb-5be0-4bb3-b351-a13eeed2194f -->
# برنامه پیاده‌سازی AI Assistant و MCP Server

## هدف

ایجاد یک سیستم AI Assistant که کاربران بتوانند با آن چت کنند و دستورات را اجرا کنند، همراه با MCP Server برای ارتباط با سایر AI ها.

## ساختار کلی

### 1. ایجاد Branch جدید

- ایجاد branch `feature/ai-assistant` از آخرین commit در master
- تمام تغییرات در این branch انجام می‌شود

### 2. نصب وابستگی‌ها

- اضافه کردن به `requirements.txt`:
  - `langchain>=0.1.0`
  - `langchain-openai>=0.0.5` (برای OpenAI)
  - `langchain-anthropic>=0.1.0` (برای Anthropic Claude)
  - `langchain-huggingface>=0.0.1` (برای Hugging Face models)
  - `langchain-community>=0.0.20` (برای سایر providers)
  - `mcp>=0.1.0` (برای MCP Server)
  - `chromadb>=0.4.0` (برای RAG vector store)
  - `drf-spectacular>=0.27.0` (برای تولید OpenAPI schema)
  - `httpx>=0.25.0` (برای ارتباط با Hugging Face Spaces)

### 3. ساختار پوشه‌ها

```
construction/
├── assistant/
│   ├── __init__.py
│   ├── agent.py          # Agent اصلی
│   ├── tools.py          # Tools برای Agent
│   ├── rag.py            # RAG pipeline (در صورت نیاز)
│   ├── mcp_server.py     # MCP Server
│   ├── views.py          # Django views
│   ├── urls.py           # URL routing
│   └── templates/
│       └── assistant/
│           └── chat.html # رابط چت
```

### 4. پیاده‌سازی Agent

#### 4.1 LLM Provider Abstraction (construction/assistant/llm_providers.py)

ایجاد یک abstraction layer برای پشتیبانی از چندین LLM provider:

- `LLMProvider` base class
- `OpenAIProvider`: پشتیبانی از OpenAI GPT models
- `AnthropicProvider`: پشتیبانی از Anthropic Claude
- `HuggingFaceProvider`: پشتیبانی از Hugging Face Spaces و local models
- `LocalModelProvider`: پشتیبانی از مدل‌های محلی (Ollama, LocalAI)
- Factory pattern برای انتخاب provider بر اساس تنظیمات

هر Provider باید:

- Interface یکسان برای Agent
- پشتیبانی از Function/Tool Calling
- مدیریت API keys و endpoints
- Error handling مناسب

#### 4.2 Tools (construction/assistant/tools.py)

**فاز اول - فقط خواندن + ایجاد:**

- `create_expense`: ایجاد هزینه جدید
- `get_expense`: دریافت اطلاعات هزینه
- `list_expenses`: لیست هزینه‌ها (با فیلتر)
- `get_investor_info`: اطلاعات سرمایه‌گذار
- `list_periods`: لیست دوره‌ها
- `get_project_stats`: آمار پروژه
- `search_expenses`: جستجوی هزینه‌ها

**نکته:** در فاز اول فقط Create operations. Update و Delete در فازهای بعدی.

هر Tool باید:

- از `@tool` decorator استفاده کند
- اطلاعات پروژه جاری را از session دریافت کند
- خطاها را به صورت مناسب handle کند
- پاسخ‌های فارسی و مفید برگرداند
- Validation مناسب برای input ها

#### 4.3 RAG Pipeline (construction/assistant/rag.py)

**هدف:** یادگیری API و مستندات برای پاسخ به سوالات

- استفاده از drf-spectacular برای تولید OpenAPI schema
- پردازش schema با LangChain OpenAPISpecLoader
- ایجاد embeddings با استفاده از Hugging Face models (برای کاهش هزینه)
- ذخیره در ChromaDB vector store
- Integration با Agent برای:
  - پاسخ به سوالات درباره API
  - یادگیری ساختار endpoint ها
  - تولید کد نمونه
  - راهنمای استفاده

**نکته مهم:** RAG می‌تواند به تنهایی برای اجرای عملیات استفاده شود (بدون MCP) با استفاده از Function Calling. اما MCP برای استانداردسازی و یکپارچه‌سازی بهتر است.

#### 4.4 Agent (construction/assistant/agent.py)

- استفاده از LangChain Agent با پشتیبانی از چندین provider
- Agent Factory برای انتخاب provider مناسب
- Prompt engineering برای پاسخ‌های فارسی
- Context management:
  - پروژه جاری از session
  - کاربر جاری
  - تاریخچه گفتگو (اختیاری)
- Integration با RAG برای دسترسی به مستندات
- Integration با Tools برای اجرای عملیات

### 5. Django Integration

#### 5.1 Views (construction/assistant/views.py)

- `chat_view`: صفحه چت
- `chat_api`: API endpoint برای ارسال پیام
- `chat_history`: تاریخچه چت (اختیاری)

#### 5.2 URLs (construction/assistant/urls.py)

- `/assistant/chat/` - صفحه چت
- `/assistant/api/` - API endpoint
- `/assistant/history/` - تاریخچه (اختیاری)

#### 5.3 Template (construction/assistant/templates/assistant/chat.html)

- رابط چت با UI مناسب
- نمایش پیام‌های کاربر و Assistant
- ارسال پیام با Enter یا دکمه
- Loading state
- Error handling

### 6. MCP Server (construction/assistant/mcp_server.py)

#### 6.1 MCP Tools

- `get_project_info`: دریافت اطلاعات پروژه
- `list_projects`: لیست پروژه‌ها
- `get_expense`: دریافت هزینه
- `create_expense`: ایجاد هزینه
- `get_investor_info`: اطلاعات سرمایه‌گذار
- `get_transaction_info`: اطلاعات تراکنش
- `get_project_statistics`: آمار پروژه

#### 6.2 MCP Resources

- `project://{id}` - اطلاعات پروژه
- `expense://{id}` - اطلاعات هزینه
- `investor://{id}` - اطلاعات سرمایه‌گذار

#### 6.3 MCP Prompts

- `project_summary` - خلاصه پروژه
- `expense_analysis` - تحلیل هزینه‌ها

### 7. تنظیمات

#### 7.1 Settings (construction_project/settings.py)

- اضافه کردن `construction.assistant` به INSTALLED_APPS
- تنظیمات LLM (API key از environment variables)
- تنظیمات MCP Server

#### 7.2 Environment Variables (.env)

- `OPENAI_API_KEY` (یا ANTHROPIC_API_KEY)
- `MCP_SERVER_PORT` (اختیاری)

### 8. امنیت

- Authentication required برای تمام endpoints
- Permission checking در Tools
- Rate limiting برای API calls
- Input validation و sanitization

### 9. تست

- Unit tests برای Tools
- Integration tests برای Agent
- Tests برای MCP Server

### 10. مستندات

- README.md برای assistant app
- مستندات MCP Server
- مثال‌های استفاده

## فایل‌های اصلی که ایجاد/تغییر می‌یابند

### فایل‌های جدید:

- `construction/assistant/__init__.py`
- `construction/assistant/agent.py`
- `construction/assistant/tools.py`
- `construction/assistant/rag.py` (اختیاری)
- `construction/assistant/mcp_server.py`
- `construction/assistant/views.py`
- `construction/assistant/urls.py`
- `construction/assistant/templates/assistant/chat.html`
- `construction/assistant/tests.py`

### فایل‌های تغییر یافته:

- `requirements.txt` - اضافه کردن dependencies
- `construction_project/settings.py` - اضافه کردن app و تنظیمات
- `construction/urls.py` - اضافه کردن URL patterns
- `.env.example` - اضافه کردن environment variables

## مراحل اجرا

1. ایجاد branch از master
2. نصب dependencies
3. ایجاد ساختار پوشه‌ها
4. پیاده‌سازی Tools
5. پیاده‌سازی Agent
6. پیاده‌سازی Views و Templates
7. پیاده‌سازی MCP Server
8. Integration و Testing
9. مستندات

## نکات مهم

- تمام کدها باید به فارسی پاسخ دهند
- استفاده از پروژه جاری از session
- Error handling مناسب
- Logging برای debugging
- پشتیبانی از چند LLM provider (قابل توسعه)
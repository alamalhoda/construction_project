# AI Assistant برای پروژه ساخت‌وساز

این ماژول یک دستیار هوشمند AI برای سیستم مدیریت پروژه ساخت‌وساز فراهم می‌کند.

## ویژگی‌ها

- **چت تعاملی**: کاربران می‌توانند با دستیار چت کنند و دستورات را اجرا کنند
- **پشتیبانی از چند LLM Provider**: OpenAI, Anthropic, Hugging Face, Local models
- **RAG Pipeline**: یادگیری API و مستندات برای پاسخ به سوالات
- **MCP Server**: ارتباط با سایر AI ها از طریق Model Context Protocol
- **Tools**: ابزارهای مختلف برای ایجاد و خواندن اطلاعات

## نصب

### 1. نصب Dependencies

```bash
pip install -r requirements.txt
```

### 2. تنظیمات Environment Variables

در فایل `.env` اضافه کنید:

```bash
# OpenAI (پیش‌فرض)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4

# یا Anthropic
# ANTHROPIC_API_KEY=your_anthropic_api_key
# ANTHROPIC_MODEL=claude-3-sonnet-20240229

# یا Google Gemini
# GOOGLE_API_KEY=your_google_api_key
# GEMINI_MODEL=gemini-pro

# یا OpenRouter (unified interface for multiple LLMs)
# OPENROUTER_API_KEY=your_openrouter_api_key
# OPENROUTER_MODEL=openai/gpt-4  # یا anthropic/claude-3-sonnet, google/gemini-pro

# یا Hugging Face
# HUGGINGFACE_API_KEY=your_huggingface_api_key
# HUGGINGFACE_ENDPOINT=https://your-space.hf.space

# یا Local Model
# LOCAL_MODEL_URL=http://localhost:11434
# LOCAL_MODEL_NAME=llama2

# انتخاب Provider
AI_ASSISTANT_PROVIDER=openai  # openai, anthropic, gemini, openrouter, huggingface, local
```

### 3. تنظیمات Django

در `settings.py` اطمینان حاصل کنید که:

```python
INSTALLED_APPS = [
    # ...
    'drf_spectacular',
    'assistant',
]

REST_FRAMEWORK = {
    # ...
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Construction Project API',
    'DESCRIPTION': 'API documentation',
    'VERSION': '1.0.0',
}
```

## استفاده

### 1. دسترسی به رابط چت

```
http://localhost:8000/assistant/chat/
```

### 2. استفاده از API

```python
from assistant.agent import create_assistant_agent

# ایجاد Agent
agent = create_assistant_agent(request=request)

# ارسال پیام
result = agent.invoke("یک هزینه با رقم 1000000 و در دوره 1 برای مدیر پروژه ایجاد کن")
print(result['output'])
```

### 3. استفاده از MCP Server

```python
from assistant.mcp_server import create_mcp_server

# ایجاد MCP Server
server = create_mcp_server(project_id=1)

# اجرای Server
import asyncio
asyncio.run(server.run())
```

## Tools موجود

- `create_expense`: ایجاد هزینه جدید
- `get_expense`: دریافت اطلاعات هزینه
- `list_expenses`: لیست هزینه‌ها
- `get_investor_info`: اطلاعات سرمایه‌گذار
- `list_periods`: لیست دوره‌ها
- `get_project_stats`: آمار پروژه
- `search_expenses`: جستجوی هزینه‌ها

## RAG Pipeline

RAG Pipeline برای یادگیری API و مستندات استفاده می‌شود:

```python
from assistant.rag import get_rag_pipeline

# ایجاد RAG Pipeline
rag = get_rag_pipeline()

# تولید schema
rag.generate_schema()

# ایجاد embeddings
rag.create_embeddings()

# جستجو
results = rag.search("چطور Expense ایجاد کنم؟")
```

## MCP Server

MCP Server برای ارتباط با سایر AI ها:

### Tools
- `get_project_info`: دریافت اطلاعات پروژه
- `list_projects`: لیست پروژه‌ها
- `get_expense`: دریافت هزینه
- `create_expense`: ایجاد هزینه
- `get_investor_info`: اطلاعات سرمایه‌گذار
- `get_transaction_info`: اطلاعات تراکنش
- `get_project_statistics`: آمار پروژه

### Resources
- `project://{id}`: اطلاعات پروژه
- `expense://{id}`: اطلاعات هزینه
- `investor://{id}`: اطلاعات سرمایه‌گذار

### Prompts
- `project_summary`: خلاصه پروژه
- `expense_analysis`: تحلیل هزینه‌ها

## مثال‌های استفاده

### ایجاد هزینه

```
کاربر: یک هزینه با رقم 1000000 و در دوره 1 برای مدیر پروژه ایجاد کن

Assistant: ✅ هزینه با موفقیت ایجاد شد!
📋 شناسه: #123
💰 مبلغ: 1,000,000 تومان
📅 دوره: مرداد 1403
👤 نوع: مدیر پروژه
```

### دریافت اطلاعات

```
کاربر: لیست دوره‌ها را نشان بده

Assistant: 📅 لیست دوره‌های پروژه:
  • مرداد 1403 (شناسه: 1)
  • شهریور 1403 (شناسه: 2)
  • مهر 1403 (شناسه: 3)
```

## توسعه

### اضافه کردن Tool جدید

1. در `tools.py` یک function جدید با decorator `@tool` اضافه کنید
2. در `agent.py` در متد `_create_tools` آن را اضافه کنید

### اضافه کردن Provider جدید

1. در `llm_providers.py` یک کلاس جدید از `LLMProvider` ایجاد کنید
2. در `LLMProviderFactory` آن را اضافه کنید

## تست

```bash
python manage.py test assistant
```

## مستندات بیشتر

برای اطلاعات بیشتر به مستندات اصلی پروژه مراجعه کنید.


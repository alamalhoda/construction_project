# Assistant - تولید Tools و رابط کاربری برای دستیار هوش مصنوعی

این ماژول وظیفه تولید فایل‌های Tools و مستندات RAG برای سرویس مستقل دستیار هوش مصنوعی را بر عهده دارد. همچنین رابط کاربری چت را برای ارتباط کاربران با دستیار فراهم می‌کند.

## ویژگی‌ها

- **تولید خودکار Tools**: تولید Tools از OpenAPI Schema یا Models/ViewSets
- **تولید مستندات RAG**: تولید مستندات قابل استفاده در RAG Pipeline
- **رابط کاربری چت**: صفحه چت برای ارتباط کاربران با دستیار هوش مصنوعی
- **پشتیبانی از نسخه Django و Standalone**: تولید Tools برای استفاده در Django یا سرویس مستقل

## ساختار

```
assistant/
├── generators/              # Generator های Tools
│   ├── schema_tool_generator.py    # تولید از OpenAPI Schema
│   ├── model_tool_generator.py      # تولید از Models/ViewSets
│   └── TOOL_GENERATORS_README.md    # راهنمای Generators
├── generated/              # فایل‌های تولید شده
│   ├── generated_tools_from_schema.py
│   ├── generated_tools_from_models.py
│   └── tool_documents_for_rag.json
├── views.py                # View های Django برای رابط کاربری
├── urls.py                 # URL patterns
├── templates/              # قالب‌های HTML
│   └── assistant/chat.html
├── viewset_helper.py       # Helper برای فراخوانی ViewSets
├── jwt_helper.py           # Helper برای تولید JWT Token
└── management/commands/    # Management Commands
    └── generate_tools.py   # دستور تولید Tools
```

## نصب

### 1. نصب Dependencies

```bash
pip install -r requirements.txt
```

### 2. تنظیمات Django

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

### 3. تنظیمات Environment Variables

برای استفاده از رابط کاربری چت، در فایل `.env` اضافه کنید:

```bash
# فعال‌سازی دستیار
AI_ASSISTANT_ENABLED=true

# URL سرویس مستقل دستیار هوش مصنوعی
AI_ASSISTANT_SERVICE_URL=http://localhost:8001
```

## استفاده

### 1. تولید Tools و مستندات RAG

#### استفاده از Management Command (توصیه می‌شود)

```bash
# تولید Tools از OpenAPI Schema (پیش‌فرض)
python manage.py generate_tools

# تولید Tools از Models/ViewSets
python manage.py generate_tools --source models

# تولید هر دو
python manage.py generate_tools --source both

# تولید برای سرویس مستقل
python manage.py generate_tools --target standalone --rag

# تولید با مسیرهای مشخص
python manage.py generate_tools \
  --output assistant/generated/my_tools.py \
  --rag \
  --rag-output assistant/generated/my_rag_docs.json
```

#### استفاده مستقیم از Generators

```bash
# تولید از OpenAPI Schema
python assistant/generators/schema_tool_generator.py

# تولید از Models
python assistant/generators/model_tool_generator.py
```

### 2. دسترسی به رابط چت

```
http://localhost:8000/assistant/chat/
```

رابط کاربری چت به صورت خودکار با سرویس مستقل دستیار هوش مصنوعی ارتباط برقرار می‌کند.

### 3. استفاده از API

```python
# ارسال درخواست به دستیار از طریق API
POST /assistant/api/
Content-Type: application/json

{
    "message": "یک هزینه با رقم 1000000 و در دوره 1 برای مدیر پروژه ایجاد کن"
}
```

## تولید Tools

### از OpenAPI Schema

این روش کامل‌ترین اطلاعات را فراهم می‌کند:

```bash
python manage.py generate_tools --source schema
```

**مزایا:**
- ✅ شامل تمام endpoints (standard و custom actions)
- ✅ شامل تمام پارامترهای requestBody
- ✅ شامل descriptions و types کامل
- ✅ شامل enum values و format ها
- ✅ شامل security requirements
- ✅ شامل response schemas

### از Models/ViewSets

این روش از ViewSets و Serializers استفاده می‌کند:

```bash
python manage.py generate_tools --source models
```

**مزایا:**
- ✅ تحلیل مستقیم ViewSets
- ✅ استفاده از Serializers برای استخراج فیلدها
- ✅ استفاده از Models برای تولید body
- ✅ پشتیبانی از custom actions

### تولید برای سرویس مستقل

برای تولید Tools که مستقیماً در سرویس مستقل قابل استفاده باشند:

```bash
python manage.py generate_tools \
  --target standalone \
  --rag \
  --standalone-output ../django_ai_assistant_service/assistant_service/tools/generated/generated_tools_from_schema.py \
  --rag-output ../django_ai_assistant_service/assistant_service/tools/generated/tool_documents_for_rag.json
```

## تفاوت نسخه Django و Standalone

### نسخه Django (پیش‌فرض)
- از `assistant.viewset_helper` استفاده می‌کند
- `request=None` parameter دارد
- sync functions هستند
- برای استفاده در برنامه اصلی Django

### نسخه Standalone
- از `assistant_service.tools.executor.HTTPToolsExecutor` استفاده می‌کند
- `api_token: str` parameter دارد (اولین parameter)
- async functions هستند
- برای استفاده در سرویس مستقل

## فایل‌های تولید شده

### generated_tools_from_schema.py
فایل Python شامل تمام Tools تولید شده از OpenAPI Schema.

### generated_tools_from_models.py
فایل Python شامل تمام Tools تولید شده از Models/ViewSets.

### tool_documents_for_rag.json
مستندات JSON برای استفاده در RAG Pipeline که شامل:
- نام Tool
- توضیحات
- پارامترها
- مثال‌های استفاده

## توسعه

### اضافه کردن Tool جدید

Tools به صورت خودکار از OpenAPI Schema یا ViewSets تولید می‌شوند. برای اضافه کردن Tool جدید:

1. ViewSet یا API endpoint جدید را در پروژه ایجاد کنید
2. OpenAPI Schema را به‌روزرسانی کنید (با `python manage.py spectacular --file schema.json`)
3. Tools را دوباره تولید کنید: `python manage.py generate_tools`

## مستندات بیشتر

- [STRUCTURE.md](STRUCTURE.md) - ساختار کامل پوشه Assistant
- [generators/TOOL_GENERATORS_README.md](generators/TOOL_GENERATORS_README.md) - راهنمای Generators
- [generators/STANDALONE_TOOLS_GENERATION.md](generators/STANDALONE_TOOLS_GENERATION.md) - راهنمای تولید Tools برای سرویس مستقل

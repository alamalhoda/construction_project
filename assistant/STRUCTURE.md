# ساختار پوشه Assistant

این سند ساختار پوشه `assistant/` را توضیح می‌دهد.

## 📁 ساختار کلی

```
assistant/
├── __init__.py                 # ماژول اصلی
├── views.py                    # View های Django برای رابط کاربری
├── urls.py                     # URL patterns
├── viewset_helper.py           # Helper برای فراخوانی ViewSets
├── jwt_helper.py               # Helper برای تولید JWT Token
├── apps.py                     # Django app config
├── README.md                   # مستندات اصلی
├── STRUCTURE.md                # این فایل
│
├── generated/                  # فایل‌های تولید شده (auto-generated)
│   ├── __init__.py
│   ├── generated_tools_from_schema.py    # Tools تولید شده از OpenAPI Schema
│   ├── generated_tools_from_models.py     # Tools تولید شده از Models
│   ├── tool_documents_for_rag.json        # مستندات RAG
│   └── tool_documents_for_rag_readable.json  # مستندات RAG (قابل خواندن)
│
├── generators/                 # Generator های Tools
│   ├── __init__.py
│   ├── schema_tool_generator.py # Generator از OpenAPI Schema
│   ├── model_tool_generator.py  # Generator از Models/ViewSets
│   ├── TOOL_GENERATORS_README.md # راهنمای استفاده از Generators
│   └── STANDALONE_TOOLS_GENERATION.md # راهنمای تولید Tools برای سرویس مستقل
│
├── templates/                   # قالب‌های HTML
│   └── assistant/
│       └── chat.html          # صفحه چت با دستیار
│
├── management/                  # Django management commands
│   └── commands/
│       └── generate_tools.py  # دستور تولید Tools و مستندات RAG
│
├── tests/                       # تست‌های واحد
│   ├── __init__.py
│   └── README.md               # راهنمای تست‌ها
│
└── logs/                        # فایل‌های لاگ
```

## 📝 توضیحات پوشه‌ها

### فایل‌های اصلی

- **views.py**: View های Django برای رابط کاربری چت و API endpoint برای ارسال درخواست به سرویس مستقل دستیار
- **urls.py**: URL patterns برای دسترسی به رابط کاربری و API
- **viewset_helper.py**: Helper برای فراخوانی ViewSet methods از طریق HTTP
- **jwt_helper.py**: Helper برای تولید JWT Token برای احراز هویت در سرویس مستقل

### پوشه `generated/`

فایل‌های تولید شده به صورت خودکار. این فایل‌ها نباید به صورت دستی ویرایش شوند.

- **generated_tools_from_schema.py**: Tools تولید شده از OpenAPI Schema (استفاده می‌شود)
- **generated_tools_from_models.py**: Tools تولید شده از Models/ViewSets (آماده برای استفاده)
- **tool_documents_for_rag.json**: مستندات JSON برای RAG Pipeline
- **tool_documents_for_rag_readable.json**: مستندات JSON قابل خواندن برای RAG Pipeline

### پوشه `generators/`

Generator های Tools که برای تولید فایل‌های `generated/` استفاده می‌شوند.

- **schema_tool_generator.py**: تولید Tools از OpenAPI Schema
- **model_tool_generator.py**: تولید Tools از Models/ViewSets
- **TOOL_GENERATORS_README.md**: راهنمای استفاده از Generators
- **STANDALONE_TOOLS_GENERATION.md**: راهنمای تولید Tools برای سرویس مستقل

### پوشه `templates/`

قالب‌های HTML برای رابط کاربری.

- **assistant/chat.html**: صفحه چت با دستیار هوش مصنوعی

### پوشه `management/commands/`

Django Management Commands.

- **generate_tools.py**: دستور برای تولید Tools و مستندات RAG

### پوشه `tests/`

تست‌های واحد برای Assistant.

## 🔄 نحوه استفاده

### تولید Tools جدید

#### استفاده از Management Command (توصیه می‌شود)

```bash
# تولید از OpenAPI Schema (پیش‌فرض)
python manage.py generate_tools

# تولید از Models/ViewSets
python manage.py generate_tools --source models

# تولید هر دو
python manage.py generate_tools --source both

# تولید برای سرویس مستقل با مستندات RAG
python manage.py generate_tools --target standalone --rag
```

#### استفاده مستقیم از Generators

```bash
# تولید از OpenAPI Schema
python assistant/generators/schema_tool_generator.py

# تولید از Models
python assistant/generators/model_tool_generator.py
```

### دسترسی به رابط کاربری

```
http://localhost:8000/assistant/chat/
```

## 🔄 جریان کار

1. **تولید OpenAPI Schema**: با استفاده از `drf-spectacular`
   ```bash
   python manage.py spectacular --file schema.json --format openapi-json
   ```

2. **تولید Tools**: با استفاده از Management Command
   ```bash
   python manage.py generate_tools
   ```

3. **استفاده در سرویس مستقل**: فایل‌های تولید شده به سرویس مستقل کپی می‌شوند

4. **رابط کاربری**: کاربران از طریق صفحه چت با دستیار ارتباط برقرار می‌کنند

## 📚 مستندات بیشتر

- [README.md](README.md) - مستندات اصلی
- [generators/TOOL_GENERATORS_README.md](generators/TOOL_GENERATORS_README.md) - راهنمای Generators
- [generators/STANDALONE_TOOLS_GENERATION.md](generators/STANDALONE_TOOLS_GENERATION.md) - راهنمای تولید Tools برای سرویس مستقل
- [tests/README.md](tests/README.md) - راهنمای تست‌های واحد

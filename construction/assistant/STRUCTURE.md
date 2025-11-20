# ساختار پوشه Assistant

این سند ساختار پوشه `construction/assistant/` را توضیح می‌دهد.

## 📁 ساختار کلی

```
construction/assistant/
├── __init__.py                 # ماژول اصلی
├── agent.py                    # کلاس اصلی Agent
├── llm_providers.py            # پشتیبانی از چند LLM Provider
├── tools.py                    # ابزارهای دستی (manual tools)
├── views.py                    # View های Django
├── urls.py                     # URL patterns
├── mcp_server.py               # MCP Server برای ارتباط با AI های دیگر
├── rag.py                      # RAG Pipeline برای یادگیری API
├── viewset_helper.py           # Helper برای ViewSets
├── apps.py                     # Django app config
├── README.md                   # مستندات اصلی
│
├── generated/                  # فایل‌های تولید شده (auto-generated)
│   ├── __init__.py
│   ├── generated_tools_from_schema.py    # Tools تولید شده از OpenAPI Schema
│   └── generated_tools_from_models.py     # Tools تولید شده از Models
│
├── generators/                 # Generator های Tools
│   ├── __init__.py
│   ├── tool_generator.py       # Generator اصلی (deprecated)
│   ├── schema_tool_generator.py # Generator از OpenAPI Schema
│   ├── model_tool_generator.py  # Generator از Models/ViewSets
│   └── TOOL_GENERATORS_README.md # راهنمای استفاده از Generators
│
├── scripts/                     # اسکریپت‌های تست و ابزار
│   ├── test_agent_with_llm.py  # تست Agent با LLM واقعی
│   ├── test_llm_providers.py   # تست تمام Provider های LLM
│   ├── test_all_providers.py   # تست دسترسی به مدل‌های مختلف
│   ├── debug_tools.py          # اسکریپت debug برای مشاهده Tools
│   └── README_AI_ASSISTANT_TESTS.md # راهنمای تست‌ها
│
├── docs/                        # مستندات
│   └── TEST_PROVIDERS_README.md # راهنمای تست Provider ها
│
├── tests/                       # تست‌های واحد
│   ├── __init__.py
│   ├── test_agent_tools.py     # تست Tools
│   └── README.md               # راهنمای تست‌ها
│
├── templates/                   # قالب‌های HTML
│   └── assistant/
│       └── chat.html          # صفحه چت
│
├── management/                  # Django management commands
│   └── commands/
│       └── setup_rag.py        # دستور setup برای RAG
│
└── logs/                        # فایل‌های لاگ
```

## 📝 توضیحات پوشه‌ها

### فایل‌های اصلی

- **agent.py**: کلاس اصلی `ConstructionAssistantAgent` که Agent را مدیریت می‌کند
- **llm_providers.py**: پشتیبانی از چند LLM Provider (OpenAI, Anthropic, Gemini, OpenRouter, HuggingFace, Local)
- **tools.py**: ابزارهای دستی که Agent می‌تواند استفاده کند
- **views.py**: View های Django برای رابط کاربری
- **mcp_server.py**: MCP Server برای ارتباط با سایر AI ها
- **rag.py**: RAG Pipeline برای یادگیری API و مستندات

### پوشه `generated/`

فایل‌های تولید شده به صورت خودکار. این فایل‌ها نباید به صورت دستی ویرایش شوند.

- **generated_tools_from_schema.py**: Tools تولید شده از OpenAPI Schema (استفاده می‌شود)
- **generated_tools_from_models.py**: Tools تولید شده از Models/ViewSets (آماده برای استفاده)

### پوشه `generators/`

Generator های Tools که برای تولید فایل‌های `generated/` استفاده می‌شوند.

- **schema_tool_generator.py**: تولید Tools از OpenAPI Schema
- **model_tool_generator.py**: تولید Tools از Models/ViewSets
- **tool_generator.py**: Generator قدیمی (deprecated)

### پوشه `scripts/`

اسکریپت‌های تست و ابزارهای کمکی.

- **test_agent_with_llm.py**: تست Agent با LLM واقعی
- **test_llm_providers.py**: تست تمام Provider های LLM
- **test_all_providers.py**: تست دسترسی به مدل‌های مختلف
- **debug_tools.py**: مشاهده Tools معرفی شده به AI

### پوشه `docs/`

مستندات مربوط به Assistant.

### پوشه `tests/`

تست‌های واحد برای Assistant.

## 🔄 نحوه استفاده

### تولید Tools جدید

```bash
# تولید از OpenAPI Schema
python construction/assistant/generators/schema_tool_generator.py

# تولید از Models
python construction/assistant/generators/model_tool_generator.py
```

### اجرای تست‌ها

```bash
# تست Agent
python construction/assistant/scripts/test_agent_with_llm.py

# تست Provider ها
python construction/assistant/scripts/test_llm_providers.py

# تست دسترسی به مدل‌ها
python construction/assistant/scripts/test_all_providers.py
```

### Debug Tools

```bash
python construction/assistant/scripts/debug_tools.py
```

## 📚 مستندات بیشتر

- [README.md](README.md) - مستندات اصلی
- [generators/TOOL_GENERATORS_README.md](generators/TOOL_GENERATORS_README.md) - راهنمای Generators
- [scripts/README_AI_ASSISTANT_TESTS.md](scripts/README_AI_ASSISTANT_TESTS.md) - راهنمای تست‌ها
- [docs/TEST_PROVIDERS_README.md](docs/TEST_PROVIDERS_README.md) - راهنمای تست Provider ها
- [tests/README.md](tests/README.md) - راهنمای تست‌های واحد


# راهنمای تولید Tools برای سرویس مستقل

این راهنما نحوه تولید Tools برای سرویس مستقل دستیار هوش مصنوعی را توضیح می‌دهد.

## تولید Tools برای سرویس مستقل

برای تولید Tools که مستقیماً در سرویس مستقل قابل استفاده باشند:

```bash
cd construction_project
python assistant/generators/schema_tool_generator.py \
  --target standalone \
  --output ../django_ai_assistant_service/assistant_service/tools/generated/generated_tools_from_schema.py
```

## تولید مستندات RAG برای سرویس مستقل

برای تولید مستندات RAG که در سرویس مستقل استفاده می‌شوند:

```bash
python assistant/generators/schema_tool_generator.py \
  --target standalone \
  --rag \
  --rag-output ../django_ai_assistant_service/assistant_service/tools/generated/tool_documents_for_rag.json
```

## تولید همزمان Tools و مستندات RAG

```bash
python assistant/generators/schema_tool_generator.py \
  --target standalone \
  --output ../django_ai_assistant_service/assistant_service/tools/generated/generated_tools_from_schema.py \
  --rag \
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

## مثال خروجی Standalone

```python
@tool
async def expense_list(api_token: str, **kwargs) -> str:
    """
    دریافت لیست تمام هزینه‌های پروژه جاری
    ...
    """
    try:
        from assistant_service.tools.executor import HTTPToolsExecutor
        from assistant_service.tools.response_formatter import format_response
        from django.conf import settings
        
        executor = HTTPToolsExecutor(
            base_url=getattr(settings, 'MAIN_APP_URL', 'http://localhost:8000'),
            api_token=api_token
        )
        
        result = await executor.execute(
            method='GET',
            path='/api/v1/Expense/',
            params=kwargs if kwargs else None
        )
        
        return format_response(result)
    except Exception as e:
        return f"❌ خطا: {str(e)}"
```

## نکات مهم

1. **api_token**: همیشه اولین parameter است و required است
2. **async**: تمام tools در نسخه standalone async هستند
3. **HTTPToolsExecutor**: از این executor برای ارتباط با برنامه اصلی استفاده می‌شود
4. **format_response**: از این function برای تبدیل response به string استفاده می‌شود

## استفاده در سرویس مستقل

بعد از تولید، فایل‌ها در مسیر زیر قرار می‌گیرند:
- Tools: `django_ai_assistant_service/assistant_service/tools/generated/generated_tools_from_schema.py`
- RAG Docs: `django_ai_assistant_service/assistant_service/tools/generated/tool_documents_for_rag.json`

سپس در `loader.py` می‌توانید از این tools استفاده کنید.

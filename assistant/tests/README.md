# تست‌های Agent و ابزارها

این پوشه شامل تست‌های جامع برای Agent و ابزارهای تولید شده است.

## 📋 فایل‌های تست

- `test_agent_tools.py`: تست‌های جامع برای Agent و ابزارها

## 🧪 نحوه اجرای تست‌ها

### روش 1: استفاده از Django test runner (توصیه می‌شود)

```bash
source env/bin/activate
python3 manage.py test assistant.tests.test_agent_tools --verbosity=2
```

### روش 2: اجرای مستقیم فایل

```bash
source env/bin/activate
python3 construction/assistant/tests/test_agent_tools.py
```

## 📊 تست‌های موجود

### AgentToolsTestCase

1. **test_agent_creation**: تست ساخت Agent
2. **test_tools_count**: تست تعداد ابزارها (باید 115 ابزار باشد)
3. **test_tools_categories**: تست دسته‌بندی ابزارها
4. **test_expense_list_tool**: تست ابزار expense_list
5. **test_project_list_tool**: تست ابزار project_list
6. **test_investor_list_tool**: تست ابزار investor_list
7. **test_transaction_list_tool**: تست ابزار transaction_list
8. **test_period_list_tool**: تست ابزار period_list
9. **test_tools_have_request_parameter**: تست اینکه ابزارها request parameter دارند
10. **test_tools_from_generated_module**: تست import شدن ابزارها از generated_tools_from_schema
11. **test_tool_wrapper_functions**: تست wrapper functions
12. **test_all_critical_tools_exist**: تست وجود ابزارهای مهم
13. **test_tools_error_handling**: تست مدیریت خطا

### AgentIntegrationTestCase

1. **test_agent_with_real_data**: تست Agent با داده‌های واقعی

## 🔍 چرا از LLM استفاده نمی‌کنیم؟

در تست‌های فعلی، ما **ابزارها را مستقیماً** فراخوانی می‌کنیم بدون استفاده از LLM. این کار به دلایل زیر انجام می‌شود:

### 1. تست سریع‌تر
- بدون نیاز به API calls به LLM provider
- بدون نیاز به API keys
- اجرای سریع‌تر تست‌ها

### 2. تست دقیق‌تر
- می‌توانیم مستقیماً ابزارها را تست کنیم
- می‌توانیم ورودی‌ها و خروجی‌ها را کنترل کنیم
- می‌توانیم edge cases را بهتر تست کنیم

### 3. تست مستقل از LLM
- تست‌ها حتی اگر LLM provider در دسترس نباشد کار می‌کنند
- تست‌ها وابسته به سرویس‌های خارجی نیستند

### 4. نحوه تست

ما ابزارها را به صورت زیر تست می‌کنیم:

```python
# پیدا کردن ابزار
expense_list_tool = None
for tool_obj in agent.tools:
    if hasattr(tool_obj, 'name') and tool_obj.name == 'expense_list':
        expense_list_tool = tool_obj
        break

# فراخوانی مستقیم function
if hasattr(expense_list_tool, 'func'):
    result = expense_list_tool.func(request=request)
    # بررسی نتیجه
    assert isinstance(result, str)
    assert len(result) > 0
```

این روش مستقیماً `func` ابزار را فراخوانی می‌کند که همان function اصلی است که با `@tool` decorator شده است.

## 🚀 تست با LLM (اختیاری)

اگر می‌خواهید Agent را با LLM تست کنید، می‌توانید یک تست جداگانه اضافه کنید:

```python
def test_agent_with_llm(self):
    """تست Agent با LLM (نیاز به API key)"""
    # تنظیم API key
    import os
    if not os.getenv('OPENAI_API_KEY'):
        self.skipTest("نیاز به OPENAI_API_KEY")
    
    # ایجاد Agent با LLM
    agent = ConstructionAssistantAgent(
        request=self.request,
        provider_type='openai',
        use_rag=False
    )
    
    # تست با یک سوال واقعی
    result = agent.invoke("لیست هزینه‌ها را نشان بده")
    self.assertTrue(result.get('success', False))
```

## 📝 نکات مهم

1. **تست‌ها از دیتابیس تست استفاده می‌کنند**: هر تست یک دیتابیس جداگانه دارد
2. **تست‌ها مستقل هستند**: هر تست داده‌های خود را می‌سازد
3. **تست‌ها سریع هستند**: بدون نیاز به LLM، تست‌ها در چند ثانیه اجرا می‌شوند

## ✅ نتیجه تست‌ها

اگر همه تست‌ها موفق باشند، باید خروجی زیر را ببینید:

```
----------------------------------------------------------------------
Ran 14 tests in 14.462s

OK
```

## 🔧 عیب‌یابی

اگر تست‌ها ناموفق بودند:

1. بررسی کنید که Django به درستی تنظیم شده است
2. بررسی کنید که migrations اجرا شده‌اند
3. بررسی کنید که تمام dependencies نصب شده‌اند
4. لاگ‌های خطا را بررسی کنید

## 📚 منابع بیشتر

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [LangChain Tools Documentation](https://python.langchain.com/docs/modules/tools/)


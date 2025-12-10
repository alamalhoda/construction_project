# راهنمای سرویس مستقل AI Assistant

این سند نحوه راه‌اندازی، پیکربندی و اتصال برنامه اصلی (`construction_project`) به سرویس مستقل دستیار هوشمند (`ai_assistant_service`) را توضیح می‌دهد. برنامه اصلی بدون سرویس دستیار نیز به‌طور کامل کار می‌کند و در صورت عدم دسترس‌بودن دستیار، رابط چت به‌صورت امن و شفاف غیرفعال می‌شود.

## نمای کلی
- **برنامه اصلی (Django):** `construction_project/`
- **سرویس دستیار (FastAPI):** `ai_assistant_service/`
- **ارتباط:** REST API + JWT
- **حالت‌های کاری برنامه اصلی:**  
  - اگر `AI_ASSISTANT_ENABLED=true` و `AI_ASSISTANT_SERVICE_URL` تنظیم باشد، پیام‌ها به سرویس دستیار ارسال می‌شود.  
  - در غیر این صورت، UI چت پیام «دستیار در دسترس نیست» نمایش می‌دهد و سایر بخش‌های سیستم بدون وابستگی کار می‌کنند.

## پیش‌نیازها
- Python 3.11+
- محیط مجازی جداگانه برای هر برنامه پیشنهاد می‌شود.
- دسترسی به کلیدهای LLM (OpenAI یا سایر Providerها) برای سرویس دستیار در صورت نیاز.

## تنظیمات برنامه اصلی (Django)
۱) فایل `.env` در ریشه `construction_project/`:
```env
# فعال/غیرفعال کردن دستیار (اختیاری)
AI_ASSISTANT_ENABLED=true
AI_ASSISTANT_SERVICE_URL=http://localhost:8001
```
> اگر این متغیرها تنظیم نشوند یا `AI_ASSISTANT_ENABLED=false` باشد، دستیار غیرفعال می‌شود و تنها UI چت پیام مناسب نمایش می‌دهد.

۲) وابستگی‌ها (قبلاً اعمال شده):
- `httpx` و `PyJWT` اضافه شده‌اند.
- وابستگی‌های AI (langchain، chromadb و …) از برنامه اصلی حذف شده‌اند.

## تنظیمات سرویس دستیار (FastAPI)
۱) مسیر پروژه: `/Users/alamalhoda/Projects/Arash_Project/djangobuilder/ai_assistant_service/`

۲) فایل `.env` (کپی از `.env.example` و تکمیل مقادیر):
```env
MAIN_APP_URL=http://localhost:8000
MAIN_APP_API_TOKEN=your_secret_token        # برای احراز هویت در برنامه اصلی (JWT shared secret)
JWT_SECRET_KEY=^l)7d*%h&db4uft@dk%h-w&nup#pu%)a!d)c7jwgoixo5_hm0$  # باید با SECRET_KEY برنامه اصلی برابر باشد
AI_ASSISTANT_PROVIDER=openai                # یا anthropic, gemini, openrouter, huggingface, local
OPENAI_API_KEY=your_openai_api_key
```

۳) نصب و اجرا:
```bash
cd /Users/alamalhoda/Projects/Arash_Project/djangobuilder/ai_assistant_service
python -m venv env && source env/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
- اسکریپت آماده: `./run.sh` (قابل اجرا پس از `chmod +x run.sh`)
- Docker (اختیاری): `docker-compose up --build`

## معماری اتصال
1. کاربر در UI چت (برنامه اصلی) پیام می‌فرستد.
2. برنامه اصلی با JWT توکن، درخواست را به `/api/v1/chat` در سرویس دستیار ارسال می‌کند.
3. سرویس دستیار با استفاده از LLM + RAG (در صورت فعال بودن) و Tools (از طریق HTTP به APIهای برنامه اصلی) پاسخ را برمی‌گرداند.
4. در صورت عدم دسترسی به سرویس دستیار، UI پیام مناسب را نشان می‌دهد و دکمه ارسال غیرفعال می‌شود.

## نکات امنیتی
- `JWT_SECRET_KEY` در سرویس دستیار باید با `SECRET_KEY` برنامه اصلی یکسان باشد.
- ارتباط داخلی بین دو سرویس می‌تواند از طریق شبکه داخلی یا HTTPS امن شود.
- در صورت عدم نیاز به دستیار، `AI_ASSISTANT_ENABLED=false` بگذارید تا وابستگی حذف شود.

## تست سلامت و دسترس‌پذیری
- سرویس دستیار: `GET http://localhost:8001/health`
- برنامه اصلی بدون دستیار: `AI_ASSISTANT_ENABLED=false` → UI چت غیرفعال می‌شود؛ سایر قابلیت‌ها فعال می‌مانند.

## فایل‌های مرتبط
- برنامه اصلی:
  - `assistant/views.py` (فراخوانی HTTP + fallback)
  - `assistant/templates/assistant/chat.html` (graceful degradation)
  - `assistant/jwt_helper.py` (تولید JWT)
  - `requirements.txt` (بدون وابستگی‌های AI؛ شامل httpx و PyJWT)
- سرویس دستیار:
  - `app/main.py`, `app/api/routes.py`
  - `app/agent/agent.py`, `app/agent/llm_providers.py`, `app/agent/system_prompt.py`
  - `app/tools/executor.py`, `app/rag/pipeline.py`
  - `.env.example`, `docker-compose.yml`, `run.sh`

## سناریوهای متداول
- **فعال‌سازی دستیار:** `AI_ASSISTANT_ENABLED=true` و `AI_ASSISTANT_SERVICE_URL` را تنظیم کنید، سپس سرویس دستیار را اجرا کنید.
- **غیرفعال‌سازی/قطع دستیار:** `AI_ASSISTANT_ENABLED=false` یا قطع سرویس دستیار؛ UI چت پیام عدم دسترس‌بودن را نمایش می‌دهد.
- **تغییر Provider:** در `.env` سرویس دستیار مقدار `AI_ASSISTANT_PROVIDER` و کلیدهای مربوط به LLM را تغییر دهید.

## جمع‌بندی
سرویس دستیار اکنون به‌صورت کامل از برنامه اصلی جدا شده و هر دو می‌توانند به‌صورت مستقل اجرا شوند. برنامه اصلی بدون دستیار نیز قابل استفاده است و تنها قابلیت چت غیرفعال می‌شود. برای استفاده از دستیار، کافی است سرویس مستقل را اجرا و متغیرهای محیطی اتصال را تنظیم کنید.

# جداسازی AI Assistant Service

این سند توضیح می‌دهد که چگونه برنامه اصلی از برنامه دستیار هوشمند جدا شده است.

## ساختار

```
construction_project/          # برنامه اصلی (Django)
├── assistant/
│   ├── views.py              # تغییر یافته - استفاده از HTTP calls
│   ├── jwt_helper.py         # جدید - تولید JWT Token
│   └── templates/assistant/chat.html  # تغییر یافته - graceful degradation
│
ai_assistant_service/          # برنامه دستیار (FastAPI) - جدید
├── app/
│   ├── main.py              # FastAPI app
│   ├── agent/               # Agent و LLM Providers
│   ├── rag/                 # RAG Pipeline
│   ├── tools/               # Tools Executor
│   └── api/                 # API Routes
```

## تنظیمات

### برنامه اصلی (.env)

```bash
# تنظیمات دستیار (اختیاری - اگر وجود نداشته باشد، دستیار غیرفعال است)
AI_ASSISTANT_ENABLED=true
AI_ASSISTANT_SERVICE_URL=http://localhost:8001
```

### برنامه دستیار (.env)

```bash
MAIN_APP_URL=http://localhost:8000
MAIN_APP_API_TOKEN=your_secret_token
JWT_SECRET_KEY=^l)7d*%h&db4uft@dk%h-w&nup#pu%)a!d)c7jwgoixo5_hm0$
AI_ASSISTANT_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
```

## استقلال برنامه اصلی

✅ **برنامه اصلی کاملاً مستقل است:**
- اگر `AI_ASSISTANT_ENABLED=false` باشد یا `AI_ASSISTANT_SERVICE_URL` تنظیم نشده باشد، دستیار غیرفعال می‌شود
- تمام API های اصلی بدون تغییر کار می‌کنند
- UI چت با graceful degradation کار می‌کند (نمایش پیام مناسب)

## نحوه اجرا

### 1. اجرای برنامه اصلی

```bash
cd construction_project
source env/bin/activate
python manage.py runserver
```

### 2. اجرای برنامه دستیار (اختیاری)

```bash
cd ai_assistant_service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## تغییرات انجام شده

### برنامه اصلی

1. ✅ `assistant/views.py`: تغییر برای استفاده از HTTP calls به برنامه دستیار
2. ✅ `assistant/jwt_helper.py`: جدید - تولید JWT Token
3. ✅ `assistant/templates/assistant/chat.html`: graceful degradation
4. ✅ `requirements.txt`: حذف وابستگی‌های AI، اضافه کردن httpx و PyJWT

### برنامه دستیار (جدید)

1. ✅ ساختار FastAPI کامل
2. ✅ Agent و LLM Providers (بدون Django)
3. ✅ HTTP Tools Executor
4. ✅ RAG Pipeline
5. ✅ JWT Authentication

## نکات مهم

1. **JWT_SECRET_KEY** در برنامه دستیار باید با **SECRET_KEY** در برنامه اصلی یکسان باشد
2. برنامه اصلی می‌تواند بدون برنامه دستیار کار کند
3. Tools از طریق HTTP calls به API های برنامه اصلی اجرا می‌شوند

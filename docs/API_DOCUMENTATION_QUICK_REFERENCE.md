# راهنمای سریع مستندات API

## 🚀 دسترسی سریع

| ابزار | آدرس | کاربرد |
|-------|------|--------|
| **Swagger UI** | `/api/swagger-ui/` | تست و مشاهده تعاملی API |
| **ReDoc** | `/api/redoc/` | مشاهده مستندات (بدون تست) |
| **Schema JSON** | `/api/schema/` | دریافت فایل JSON برای ابزارها |

---

## تفاوت‌های کلیدی

### Swagger UI
- ✅ **تست API** از داخل مرورگر
- ✅ **رابط کاربری تعاملی**
- ✅ **احراز هویت** برای تست
- ❌ فقط برای مشاهده و تست

**مثال استفاده:** تست سریع endpoint جدید

### ReDoc
- ✅ **رابط کاربری زیبا**
- ✅ **موبایل‌فرندلی**
- ✅ **خوانایی بالا**
- ❌ بدون قابلیت تست

**مثال استفاده:** نمایش مستندات به مشتری

### Schema JSON
- ✅ **فایل JSON خام**
- ✅ **Import در Postman/Insomnia**
- ✅ **تولید خودکار کد**
- ✅ **استفاده در CI/CD**
- ❌ بدون رابط کاربری

**مثال استفاده:** تولید خودکار کلاینت Python

---

## کاربردهای عملی

### 1️⃣ تست سریع API
```
1. باز کردن Swagger UI
2. پیدا کردن endpoint
3. کلیک روی "Try it out"
4. پر کردن پارامترها
5. کلیک روی "Execute"
```

### 2️⃣ Import در Postman
```
1. باز کردن Postman
2. Import → Link
3. وارد کردن: /api/schema/
4. تمام endpoint‌ها اضافه می‌شوند
```

### 3️⃣ تولید کد کلاینت

#### نصب OpenAPI Generator
```bash
# روش 1: npm (پیشنهادی)
npm install -g @openapitools/openapi-generator-cli

# روش 2: Homebrew (macOS)
brew install openapi-generator

# روش 3: Docker
docker pull openapitools/openapi-generator-cli
```

#### ساختار دستور
```bash
openapi-generator generate \
  -i <ورودی> \    # آدرس Schema JSON
  -g <زبان> \      # نوع زبان خروجی
  -o <خروجی>      # پوشه خروجی
```

#### مثال‌ها
```bash
# Python
openapi-generator generate \
  -i http://localhost:8000/api/schema/ \
  -g python \
  -o ./python-client

# JavaScript
openapi-generator generate \
  -i http://localhost:8000/api/schema/ \
  -g javascript \
  -o ./javascript-client

# TypeScript
openapi-generator generate \
  -i http://localhost:8000/api/schema/ \
  -g typescript-axios \
  -o ./typescript-client
```

#### پارامترها:
- `-i` یا `--input-spec`: آدرس Schema JSON (URL یا مسیر فایل)
- `-g` یا `--generator-name`: نام generator (زبان خروجی)
- `-o` یا `--output`: پوشه خروجی برای کد تولید شده

#### استفاده در کد Python:
```python
from openapi_client import ExpenseApi, ApiClient, Configuration

config = Configuration(host="http://localhost:8000")
api_client = ApiClient(config)
expense_api = ExpenseApi(api_client)
expenses = expense_api.expense_list()
```

#### زبان‌های پشتیبانی شده:
Python, JavaScript, TypeScript, Java, C#, Go, PHP, Ruby, Swift, Kotlin و 30+ زبان دیگر

**برای اطلاعات کامل:** [راهنمای تولید کد کلاینت](./API_DOCUMENTATION_GUIDE.md#تولید-خودکار-کد-کلاینت-با-openapi-generator)

---

## انتخاب ابزار مناسب

| نیاز | ابزار پیشنهادی |
|------|----------------|
| تست سریع API | Swagger UI |
| مستندسازی عمومی | ReDoc |
| یکپارچه‌سازی با ابزارها | Schema JSON |
| تولید کد خودکار | Schema JSON |
| تست خودکار (CI/CD) | Schema JSON |

---

## نکات مهم

⚠️ **امنیت:** در Production دسترسی را محدود کنید

🔄 **به‌روزرسانی:** Schema به صورت خودکار از کد تولید می‌شود

📝 **بهترین روش:** 
- تست: Swagger UI
- مستندسازی: ReDoc  
- یکپارچه‌سازی: Schema JSON

---

**برای اطلاعات بیشتر:** [راهنمای کامل](./API_DOCUMENTATION_GUIDE.md)


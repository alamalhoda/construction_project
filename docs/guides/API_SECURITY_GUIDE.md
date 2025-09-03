# 🔐 راهنمای امنیت API - پروژه ساختمانی

## 📋 فهرست مطالب
1. [شروع سریع](#شروع-سریع)
2. [صفحه لاگین API](#صفحه-لاگین-api)
3. [استفاده از API](#استفاده-از-api)
4. [امنیت API](#امنیت-api)
5. [مثال‌های عملی](#مثالهای-عملی)

## 🚀 شروع سریع

### 1. دسترسی به صفحه لاگین API
```
http://127.0.0.1:8000/construction/api/login/
```

### 2. ورود به API
- نام کاربری: `admin`
- رمز عبور: رمز عبور ادمین شما

### 3. دریافت Token
پس از ورود موفق، token دریافت خواهید کرد که برای دسترسی به API استفاده می‌شود.

## 🔑 صفحه لاگین API

### ویژگی‌های صفحه لاگین:
- ✅ **رابط کاربری فارسی**
- ✅ **احراز هویت امن**
- ✅ **نمایش Token**
- ✅ **کپی کردن Token**
- ✅ **ذخیره در localStorage**
- ✅ **راهنمای استفاده**

### نحوه استفاده:
1. به آدرس `/construction/api/login/` بروید
2. نام کاربری و رمز عبور را وارد کنید
3. روی دکمه "ورود" کلیک کنید
4. Token را کپی کنید
5. از Token برای دسترسی به API استفاده کنید

## 📡 استفاده از API

### آدرس‌های API:
```
Base URL: http://127.0.0.1:8000/construction/api/v1/
```

### Endpoint های اصلی:
- **Projects**: `/api/v1/Project/`
- **Investors**: `/api/v1/Investor/`
- **Transactions**: `/api/v1/Transaction/`
- **Periods**: `/api/v1/Period/`
- **Expenses**: `/api/v1/Expense/`
- **Units**: `/api/v1/Unit/`
- **Interest Rates**: `/api/v1/InterestRate/`

### Endpoint های احراز هویت:
- **ورود**: `POST /api/v1/auth/login/`
- **خروج**: `POST /api/v1/auth/logout/`
- **اطلاعات کاربر**: `GET /api/v1/auth/user/`
- **تغییر رمز عبور**: `POST /api/v1/auth/change-password/`
- **وضعیت API**: `GET /api/v1/status/`

## 🛡️ امنیت API

### ویژگی‌های امنیتی:
- ✅ **احراز هویت اجباری**: همه API ها نیاز به ورود دارند
- ✅ **Token Authentication**: استفاده از Token برای احراز هویت
- ✅ **Session Authentication**: پشتیبانی از Session
- ✅ **مجوزهای سطحی**: دسترسی بر اساس نقش کاربر
- ✅ **محدودیت IP**: امکان مسدود کردن IP های مشکوک
- ✅ **ردیابی فعالیت**: ثبت تمام فعالیت‌های API
- ✅ **Rate Limiting**: محدودیت نرخ درخواست

### سطوح دسترسی:
1. **خواندنی**: همه کاربران احراز هویت شده
2. **نوشتنی**: فقط کاربران staff
3. **ادمین**: فقط superuser ها

## 💡 مثال‌های عملی

### 1. ورود به API
```bash
curl -X POST http://127.0.0.1:8000/construction/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

**پاسخ:**
```json
{
  "success": true,
  "message": "ورود موفقیت‌آمیز",
  "token": "your_token_here",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_staff": true,
    "is_superuser": true
  }
}
```

### 2. دریافت لیست پروژه‌ها
```bash
curl -X GET http://127.0.0.1:8000/construction/api/v1/Project/ \
  -H "Authorization: Token your_token_here"
```

### 3. ایجاد پروژه جدید
```bash
curl -X POST http://127.0.0.1:8000/construction/api/v1/Project/ \
  -H "Authorization: Token your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "پروژه جدید",
    "start_date_shamsi": "1403-01-01",
    "end_date_shamsi": "1403-12-29"
  }'
```

### 4. دریافت آمار تراکنش‌ها
```bash
curl -X GET http://127.0.0.1:8000/construction/api/v1/Transaction/statistics/ \
  -H "Authorization: Token your_token_here"
```

### 5. خروج از API
```bash
curl -X POST http://127.0.0.1:8000/construction/api/v1/auth/logout/ \
  -H "Authorization: Token your_token_here"
```

## 🔧 تنظیمات امنیتی

### در فایل `settings.py`:
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### مجوزهای سفارشی:
- **APISecurityPermission**: مجوز امنیتی اصلی
- **ReadOnlyPermission**: فقط خواندنی
- **AdminOnlyPermission**: فقط ادمین‌ها

## 📊 نظارت امنیتی

### لاگ‌های امنیتی:
- تمام درخواست‌های API ثبت می‌شوند
- تلاش‌های ورود ناموفق ردیابی می‌شوند
- فعالیت‌های مشکوک شناسایی می‌شوند

### بررسی لاگ‌ها:
```bash
# بررسی لاگ‌های امنیتی
tail -f logs/security.log
```

## ⚠️ نکات مهم

### ✅ کارهایی که باید انجام دهید:
1. **Token را محرمانه نگه دارید**
2. **از HTTPS در production استفاده کنید**
3. **Token را به صورت منظم تجدید کنید**
4. **لاگ‌ها را بررسی کنید**

### ❌ کارهایی که نباید انجام دهید:
1. **Token را در کد قرار ندهید**
2. **Token را در URL قرار ندهید**
3. **Token را با دیگران به اشتراک نگذارید**
4. **از HTTP در production استفاده نکنید**

## 🚨 عیب‌یابی

### مشکل 1: "Authentication credentials were not provided"
**علت**: Token ارسال نشده است
**راه‌حل**: Header `Authorization: Token your_token` را اضافه کنید

### مشکل 2: "Invalid token"
**علت**: Token نامعتبر یا منقضی شده
**راه‌حل**: دوباره وارد شوید و token جدید دریافت کنید

### مشکل 3: "Permission denied"
**علت**: کاربر دسترسی لازم را ندارد
**راه‌حل**: با کاربر ادمین وارد شوید

## 🎯 خلاصه

### برای استفاده از API:
1. **ورود**: به `/construction/api/login/` بروید
2. **Token**: token را کپی کنید
3. **استفاده**: token را در header درخواست‌ها قرار دهید
4. **امنیت**: token را محرمانه نگه دارید

### آدرس‌های مهم:
- **صفحه لاگین**: `/construction/api/login/`
- **API Base**: `/construction/api/v1/`
- **وضعیت API**: `/construction/api/v1/status/`

---

**🎉 API امنیتی شما آماده است!**

همه API ها حالا نیاز به احراز هویت دارند و فقط کاربران لاگین کرده می‌توانند به آن‌ها دسترسی داشته باشند.

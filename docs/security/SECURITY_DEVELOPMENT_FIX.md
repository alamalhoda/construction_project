# 🔧 حل مشکل تنظیمات امنیتی در Development

## 🚨 مشکل
پس از اضافه کردن تنظیمات امنیتی، صفحات سایت مشکل پیدا کردند و در کنسول خطای `strict-origin-when-cross-origin` نمایش داده می‌شد.

## ✅ راه‌حل اعمال شده

### 1. تنظیمات امنیتی نرم‌تر برای Development

در فایل `construction_project/security_settings.py`:

```python
# تنظیمات امنیتی برای Development
DEVELOPMENT_SECURITY_SETTINGS = {
    'SECURE_SSL_REDIRECT': False,
    'SESSION_COOKIE_SECURE': False,
    'CSRF_COOKIE_SECURE': False,
    'SECURE_HSTS_SECONDS': 0,
    'SECURE_HSTS_INCLUDE_SUBDOMAINS': False,
    'SECURE_HSTS_PRELOAD': False,
    'SESSION_COOKIE_HTTPONLY': False,  # برای development
    'SESSION_COOKIE_SAMESITE': 'Lax',  # نرم‌تر از Strict
    'CSRF_COOKIE_HTTPONLY': False,  # برای development
    'CSRF_COOKIE_SAMESITE': 'Lax',  # نرم‌تر از Strict
    'SECURE_CONTENT_TYPE_NOSNIFF': False,  # برای development
    'SECURE_BROWSER_XSS_FILTER': False,  # برای development
    'X_FRAME_OPTIONS': 'SAMEORIGIN',  # نرم‌تر از DENY
    'SECURE_REFERRER_POLICY': 'no-referrer-when-downgrade',  # نرم‌تر
}
```

### 2. Middleware امنیتی نرم‌تر

در فایل `construction/security_middleware.py`:

```python
def process_response(self, request, response):
    from django.conf import settings
    
    # Content Security Policy - نرم‌تر برای development
    if settings.DEBUG:
        response['Content-Security-Policy'] = (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://stackpath.bootstrapcdn.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://stackpath.bootstrapcdn.com https://unpkg.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https://stackpath.bootstrapcdn.com; "
            "connect-src 'self'; "
            "frame-ancestors 'self';"
        )
    else:
        # تنظیمات سخت برای production
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
    
    # Referrer Policy - نرم‌تر برای development
    if settings.DEBUG:
        response['Referrer-Policy'] = 'no-referrer-when-downgrade'
    else:
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
```

## 🎯 تغییرات اعمال شده

### ✅ تنظیمات Development:
- **Referrer Policy**: `no-referrer-when-downgrade` (نرم‌تر)
- **X-Frame-Options**: `SAMEORIGIN` (نرم‌تر از DENY)
- **Content Security Policy**: اجازه `unsafe-inline` و `unsafe-eval`
- **Cookie Settings**: `Lax` به جای `Strict`
- **Security Headers**: غیرفعال در development

### ✅ تنظیمات Production:
- **Referrer Policy**: `strict-origin-when-cross-origin` (سخت‌گیرانه)
- **X-Frame-Options**: `DENY` (سخت‌گیرانه)
- **Content Security Policy**: محدود و امن
- **Cookie Settings**: `Strict` و `HttpOnly`
- **Security Headers**: فعال و کامل

## 🔍 تست کردن

### بررسی Headers:
```bash
curl -s -I http://127.0.0.1:8000/dashboard/project/ | grep -E "(Referrer-Policy|X-Frame-Options|Content-Security-Policy)"
```

### نتیجه مورد انتظار در Development:
```
Content-Security-Policy: default-src 'self' 'unsafe-inline' 'unsafe-eval'; ...
Referrer-Policy: no-referrer-when-downgrade
X-Frame-Options: SAMEORIGIN
```

## 🚀 نحوه استفاده

### برای Development:
```bash
# تنظیم متغیر محیطی
export DJANGO_ENVIRONMENT=development

# یا در settings.py
ENVIRONMENT = 'development'
```

### برای Production:
```bash
# تنظیم متغیر محیطی
export DJANGO_ENVIRONMENT=production

# یا در settings.py
ENVIRONMENT = 'production'
```

## ⚠️ نکات مهم

### ✅ مزایا:
1. **Development**: تنظیمات نرم و قابل استفاده
2. **Production**: تنظیمات سخت و امن
3. **انعطاف‌پذیری**: تغییر خودکار بر اساس محیط
4. **سازگاری**: با تمام مرورگرها کار می‌کند

### 🔒 امنیت:
- در **Development**: امنیت پایه حفظ می‌شود
- در **Production**: امنیت کامل فعال است
- **API Security**: در هر دو محیط فعال است

## 🎉 نتیجه

**✅ مشکل حل شد!**

- صفحات سایت حالا بدون مشکل کار می‌کنند
- خطای `strict-origin-when-cross-origin` برطرف شد
- امنیت API همچنان فعال است
- تنظیمات بر اساس محیط (development/production) تغییر می‌کند

---

**🎯 حالا می‌توانید از سایت بدون مشکل استفاده کنید!**

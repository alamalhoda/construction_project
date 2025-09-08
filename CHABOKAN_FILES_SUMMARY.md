# خلاصه فایل‌های ایجاد شده برای استقرار در چابکان.نت

این فایل شامل لیست تمام فایل‌هایی است که برای استقرار پروژه Django شما روی چابکان.نت ایجاد شده است.

## 📁 فایل‌های اصلی

### 1. تنظیمات Django
- **`construction_project/settings_chabokan.py`** - تنظیمات Django مخصوص چابکان.نت
- **`wsgi_chabokan.py`** - فایل WSGI مخصوص چابکان.نت

### 2. وابستگی‌ها
- **`requirements-chabokan.txt`** - لیست پکیج‌های مورد نیاز برای چابکان.نت

### 3. تنظیمات سرور
- **`gunicorn.conf.py`** - تنظیمات Gunicorn برای production
- **`nginx_chabokan.conf`** - تنظیمات Nginx (اختیاری)

### 4. متغیرهای محیطی
- **`.env.chabokan`** - الگوی متغیرهای محیطی برای چابکان.نت

## 🚀 اسکریپت‌های استقرار

### 1. اسکریپت‌های اصلی
- **`deploy_chabokan.sh`** - اسکریپت خودکار استقرار
- **`start_chabokan.sh`** - اسکریپت شروع سرور

### 2. اسکریپت‌های کمکی
- **`scripts/setup_chabokan_db.py`** - تنظیم دیتابیس
- **`staticfiles_management.py`** - مدیریت static files
- **`security_chabokan.py`** - بررسی امنیت
- **`health_check.py`** - بررسی وضعیت سرور

## 📚 مستندات

### 1. راهنماهای اصلی
- **`CHABOKAN_DEPLOYMENT.md`** - راهنمای کامل استقرار
- **`CHABOKAN_FILES_SUMMARY.md`** - این فایل (خلاصه فایل‌ها)

## 🔧 نحوه استفاده

### 1. آماده‌سازی اولیه
```bash
# کپی کردن فایل متغیرهای محیطی
cp .env.chabokan .env

# ویرایش فایل .env با مقادیر واقعی
nano .env
```

### 2. اجرای استقرار
```bash
# اجرای اسکریپت استقرار
./deploy_chabokan.sh

# یا اجرای دستی
export DJANGO_SETTINGS_MODULE=construction_project.settings_chabokan
python manage.py migrate
python manage.py collectstatic --noinput
```

### 3. شروع سرور
```bash
# اجرای اسکریپت شروع
./start_chabokan.sh

# یا اجرای دستی
gunicorn --config gunicorn.conf.py wsgi_chabokan:application
```

## 🔍 بررسی وضعیت

### 1. Health Check
```bash
# بررسی وضعیت کامل
curl http://your-domain.chabokan.net/health/

# بررسی ساده
curl http://your-domain.chabokan.net/health/simple/
```

### 2. بررسی امنیت
```bash
python security_chabokan.py
```

## 📋 چک‌لیست قبل از استقرار

- [ ] فایل `.env` با مقادیر واقعی تنظیم شده
- [ ] دیتابیس PostgreSQL در چابکان.نت ایجاد شده
- [ ] اطلاعات اتصال دیتابیس در `.env` قرار داده شده
- [ ] دامنه در پنل چابکان.نت تنظیم شده
- [ ] فایل‌های کد به سرور آپلود شده
- [ ] اسکریپت `deploy_chabokan.sh` اجرا شده
- [ ] تست health check انجام شده

## ⚠️ نکات مهم

1. **امنیت**: حتماً `SECRET_KEY` را تغییر دهید
2. **دیتابیس**: از PostgreSQL استفاده کنید، نه SQLite
3. **Static Files**: حتماً `collectstatic` را اجرا کنید
4. **HTTPS**: در production از SSL استفاده کنید
5. **لاگ‌ها**: لاگ‌های خطا را بررسی کنید

## 🆘 عیب‌یابی

### مشکلات رایج
1. **خطای دیتابیس**: بررسی اطلاعات اتصال در `.env`
2. **خطای Static Files**: اجرای `collectstatic`
3. **خطای امنیت**: اجرای `security_chabokan.py`
4. **خطای شروع سرور**: بررسی پورت و تنظیمات Gunicorn

### منابع کمک
- [مستندات چابکان.نت](https://docs.chabokan.net/simple-hosting/django/)
- [مستندات Django](https://docs.djangoproject.com/)
- فایل `CHABOKAN_DEPLOYMENT.md` برای راهنمای کامل

---

**تاریخ ایجاد**: $(date)
**نسخه**: 1.0.0
**سازگار با**: Django 4.2+, Python 3.11+, Chabokan.net

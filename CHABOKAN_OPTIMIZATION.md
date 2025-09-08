# راهنمای بهینه‌سازی برای چابکان.نت

## 🚀 وضعیت فعلی

✅ **سرور با موفقیت راه‌اندازی شده!**
- Gunicorn در حال اجرا
- 100+ worker process (نیاز به بهینه‌سازی)
- سرور روی پورت 8000 listening

## ⚠️ مشکل: تعداد زیاد Worker ها

**مشکل**: تعداد worker ها خیلی زیاد است (100+)
**علت**: `multiprocessing.cpu_count()` در سرور چابکان.نت عدد بزرگی برمی‌گرداند
**راه حل**: محدود کردن تعداد worker ها

## 🔧 بهینه‌سازی‌های اعمال شده

### 1. محدود کردن Worker ها
```python
# در gunicorn.conf.py
workers = int(os.environ.get('GUNICORN_WORKERS', '3'))
```

### 2. تنظیم متغیر محیطی
```env
# در .env
GUNICORN_WORKERS=3
```

## 📊 تنظیمات پیشنهادی

### برای Development
```env
GUNICORN_WORKERS=1
```

### برای Production (چابکان.نت)
```env
GUNICORN_WORKERS=3
```

### برای سرورهای قوی‌تر
```env
GUNICORN_WORKERS=5
```

## 🔄 اعمال تغییرات

### 1. آپدیت کد
```bash
git pull origin chabokan-deployment
```

### 2. تنظیم متغیر محیطی
```bash
# در فایل .env
GUNICORN_WORKERS=3
```

### 3. راه‌اندازی مجدد
```bash
# متوقف کردن سرور فعلی
pkill -f gunicorn

# راه‌اندازی مجدد
./start.sh
```

## 🔍 بررسی عملکرد

### 1. بررسی تعداد Worker ها
```bash
ps aux | grep gunicorn | wc -l
```

### 2. بررسی استفاده از حافظه
```bash
ps aux | grep gunicorn
```

### 3. تست عملکرد
```bash
curl http://your-domain.chabokan.net/health/simple/
```

## 📈 تنظیمات پیشرفته

### 1. تنظیمات حافظه
```python
# در gunicorn.conf.py
max_requests = 1000
max_requests_jitter = 50
preload_app = True
```

### 2. تنظیمات Timeout
```python
timeout = 30
keepalive = 2
```

### 3. تنظیمات Logging
```python
accesslog = '-'
errorlog = '-'
loglevel = 'info'
```

## 🎯 نتیجه

با این تنظیمات:
- ✅ تعداد worker ها محدود می‌شود
- ✅ استفاده از حافظه بهینه می‌شود
- ✅ عملکرد سرور بهبود می‌یابد
- ✅ پایداری افزایش می‌یابد

## 📞 در صورت مشکل

1. **بررسی لاگ‌ها**: در console output چابکان.نت
2. **تست Health Check**: `/health/simple/`
3. **بررسی امنیت**: `python security_check.py`
4. **مستندات چابکان**: [docs.chabokan.net](https://docs.chabokan.net/)

---

**نکته**: بعد از اعمال تغییرات، حتماً سرور را راه‌اندازی مجدد کنید.

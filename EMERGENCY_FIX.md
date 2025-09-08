# راهنمای اضطراری حل مشکل 502

## 🚨 مشکل: 502 Bad Gateway

### مراحل فوری حل مشکل

#### 1. بررسی وضعیت فعلی
```bash
# در سرور چابکان.نت
./test_connection.sh
```

#### 2. راه‌اندازی مجدد کامل
```bash
# راه‌اندازی مجدد همه چیز
./restart.sh
```

#### 3. اگر مشکل ادامه داشت

##### گزینه A: اجرای مستقیم Gunicorn
```bash
# متوقف کردن همه چیز
pkill -f gunicorn
pkill nginx

# اجرای مستقیم Gunicorn
gunicorn construction_project.wsgi:application --bind 0.0.0.0:3000 --workers 3
```

##### گزینه B: استفاده از پورت 8000
```bash
# تغییر پورت Gunicorn به 8000
gunicorn construction_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

##### گزینه C: اجرای Django development server
```bash
# برای تست سریع
python manage.py runserver 0.0.0.0:3000
```

## 🔍 تشخیص مشکل

### بررسی‌های لازم:

1. **Gunicorn در حال اجرا است؟**
   ```bash
   ps aux | grep gunicorn
   ```

2. **پورت 3000 listening است؟**
   ```bash
   netstat -tlnp | grep :3000
   ```

3. **Gunicorn پاسخ می‌دهد؟**
   ```bash
   curl http://localhost:3000/health/simple/
   ```

4. **Nginx در حال اجرا است؟**
   ```bash
   ps aux | grep nginx
   ```

5. **پورت 80 listening است؟**
   ```bash
   netstat -tlnp | grep :80
   ```

## 🛠️ راه‌حل‌های جایگزین

### 1. استفاده از فایل Nginx ساده
```bash
# کپی کردن فایل ساده
cp nginx_simple.conf nginx.conf
```

### 2. تنظیم دستی Nginx
```bash
# ویرایش فایل Nginx
nano /etc/nginx/sites-available/default
```

### 3. تماس با پشتیبانی چابکان.نت
- ارائه لاگ‌های خطا
- توضیح مشکل
- درخواست بررسی تنظیمات

## 📞 اطلاعات مورد نیاز برای پشتیبانی

### لاگ‌های مهم:
```bash
# لاگ‌های Gunicorn
tail -20 gunicorn.log

# لاگ‌های Nginx
tail -20 /var/log/nginx/error.log

# وضعیت سیستم
./test_connection.sh
```

### اطلاعات سرور:
- دامنه: django-arash.chbk.app
- پورت Gunicorn: 3000
- پورت Nginx: 80
- وضعیت: 502 Bad Gateway

## 🎯 هدف نهایی

بعد از حل مشکل:
- ✅ سایت روی https://django-arash.chbk.app/ قابل دسترسی است
- ✅ Health check کار می‌کند
- ✅ Static files لود می‌شوند
- ✅ پنل ادمین کار می‌کند

---

**نکته**: اگر هیچ‌کدام از راه‌حل‌ها کار نکرد، با پشتیبانی چابکان.نت تماس بگیرید.

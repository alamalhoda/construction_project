# راهنمای عیب‌یابی چابکان.نت

## 🚨 مشکل 502 Bad Gateway

### علت مشکل
- **Gunicorn**: روی پورت 3000 اجرا می‌شود
- **Nginx**: روی پورت 8000 انتظار دارد
- **نتیجه**: Nginx نمی‌تواند به Gunicorn متصل شود

### راه‌حل‌های اعمال شده

#### 1. ✅ تنظیمات Nginx اصلاح شد
```nginx
# قبل
proxy_pass http://127.0.0.1:8000;

# بعد
proxy_pass http://127.0.0.1:3000;
```

#### 2. ✅ دامنه صحیح تنظیم شد
```nginx
server_name django-arash.chbk.app;
```

#### 3. ✅ فایل nginx.conf جدید ایجاد شد
- پورت صحیح (3000)
- دامنه صحیح
- تنظیمات بهینه

## 🔧 مراحل حل مشکل

### 1. آپدیت کد
```bash
git pull origin chabokan-deployment
```

### 2. آپلود فایل Nginx
فایل `nginx.conf` را در پنل چابکان.نت آپلود کنید.

### 3. راه‌اندازی مجدد
```bash
# در سرور چابکان.نت
./start.sh
```

## 🔍 بررسی وضعیت

### 1. بررسی پورت‌ها
```bash
# بررسی پورت Gunicorn
netstat -tlnp | grep :3000

# بررسی پورت Nginx
netstat -tlnp | grep :80
```

### 2. بررسی لاگ‌ها
```bash
# لاگ‌های Nginx
tail -f /var/log/nginx/error.log

# لاگ‌های Gunicorn
# در console output چابکان.نت
```

### 3. تست مستقیم Gunicorn
```bash
curl http://localhost:3000/health/simple/
```

## 📊 وضعیت مطلوب

### بعد از حل مشکل:
- ✅ Nginx روی پورت 80 listening
- ✅ Gunicorn روی پورت 3000 listening
- ✅ Nginx به Gunicorn متصل می‌شود
- ✅ سایت قابل دسترسی است

## 🆘 در صورت ادامه مشکل

### 1. بررسی تنظیمات چابکان.نت
- پورت‌های مجاز
- تنظیمات Nginx
- فایروال

### 2. تست بدون Nginx
```bash
# اجرای مستقیم Gunicorn
gunicorn construction_project.wsgi:application --bind 0.0.0.0:3000
```

### 3. تماس با پشتیبانی چابکان.نت
- ارائه لاگ‌های خطا
- توضیح مشکل
- درخواست بررسی تنظیمات

## 🎯 نکات مهم

1. **پورت 3000**: چابکان.نت از این پورت استفاده می‌کند
2. **Nginx**: باید به پورت 3000 متصل شود
3. **دامنه**: django-arash.chbk.app
4. **Health Check**: `/health/simple/`

---

**نکته**: بعد از اعمال تغییرات، حتماً سرور را راه‌اندازی مجدد کنید.

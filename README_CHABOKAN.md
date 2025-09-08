# پروژه ساخت و ساز - نسخه چابکان.نت

این برنچ مخصوص استقرار پروژه Django روی سرویس میزبانی چابکان.نت است.

## 🚀 ویژگی‌های این برنچ

- **تنظیمات بهینه شده برای چابکان.نت**: تمام تنظیمات برای production
- **نام‌های استاندارد Django**: فایل‌ها با نام‌های استاندارد Django
- **دیتابیس PostgreSQL**: آماده برای دیتابیس ابری چابکان.نت
- **امنیت پیشرفته**: تنظیمات امنیتی کامل برای production
- **Static Files Management**: با Whitenoise برای بهینه‌سازی

## 📁 ساختار فایل‌ها

```
construction_project/
├── construction_project/
│   ├── settings.py          # تنظیمات مخصوص چابکان.نت
│   ├── wsgi.py              # WSGI مخصوص چابکان.نت
│   └── urls.py              # URLs با health check
├── requirements.txt         # وابستگی‌های چابکان.نت
├── .env                     # متغیرهای محیطی
├── gunicorn.conf.py         # تنظیمات Gunicorn
├── nginx_chabokan.conf      # تنظیمات Nginx
├── deploy.sh                # اسکریپت استقرار
├── start.sh                 # اسکریپت شروع
├── security_check.py        # بررسی امنیت
└── health_check.py          # Health check endpoints
```

## 🔧 نصب و راه‌اندازی

### 1. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### 2. تنظیم متغیرهای محیطی

فایل `.env` را با مقادیر واقعی خود ویرایش کنید:

```env
# Django settings
DEBUG=False
SECRET_KEY=your-secret-key-here
DJANGO_ENVIRONMENT=production

# Database settings
DB_NAME=construction_db
DB_USER=construction_user
DB_PASSWORD=your-database-password
DB_HOST=your-database-host
DB_PORT=5432

# Domain settings
ALLOWED_HOST=your-domain.chabokan.net
TRUSTED_ORIGIN=https://your-domain.chabokan.net
```

### 3. اجرای استقرار

```bash
# اجرای اسکریپت خودکار
./deploy.sh

# یا اجرای دستی
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 4. شروع سرور

```bash
# اجرای اسکریپت شروع
./start.sh

# یا اجرای دستی
gunicorn --config gunicorn.conf.py
```

## 🔍 بررسی وضعیت

### Health Check

```bash
# بررسی وضعیت کامل
curl http://your-domain.chabokan.net/health/

# بررسی ساده
curl http://your-domain.chabokan.net/health/simple/
```

### بررسی امنیت

```bash
python security_check.py
```

## 📊 تنظیمات چابکان.نت

### 1. پنل چابکان.نت

- **Python Version**: 3.11+
- **WSGI File**: `construction_project.wsgi`
- **Requirements File**: `requirements.txt`
- **Static Files**: `/staticfiles/`
- **Media Files**: `/media/`

### 2. دیتابیس

- **نوع**: PostgreSQL
- **تنظیمات**: از طریق متغیرهای محیطی در `.env`

### 3. دامنه

- **دامنه اصلی**: `your-domain.chabokan.net`
- **دامنه‌های اضافی**: در `ALLOWED_HOSTS` تنظیم کنید

## 🔒 امنیت

### تنظیمات امنیتی فعال

- ✅ DEBUG=False
- ✅ SECRET_KEY سفارشی
- ✅ ALLOWED_HOSTS محدود
- ✅ HTTPS/SSL
- ✅ HSTS headers
- ✅ CSRF protection
- ✅ XSS protection
- ✅ Content Security Policy

### بررسی امنیت

```bash
python security_check.py
```

## 📝 لاگ‌ها

### مکان لاگ‌ها

- **Django logs**: `logs/django.log`
- **Gunicorn logs**: console output
- **Nginx logs**: `/var/log/nginx/` (در سرور)

### سطح لاگ‌ها

- **Production**: INFO level
- **Development**: DEBUG level (غیرفعال در این برنچ)

## 🚀 استقرار در چابکان.نت

### 1. آپلود کد

```bash
# آپلود از طریق Git
git push origin chabokan-deployment

# یا آپلود مستقیم فایل‌ها
```

### 2. تنظیمات سرور

1. **Python Version**: 3.11+
2. **WSGI Module**: `construction_project.wsgi`
3. **Requirements**: `requirements.txt`
4. **Static Files**: `/staticfiles/`
5. **Environment Variables**: از فایل `.env`

### 3. دیتابیس

1. ایجاد دیتابیس PostgreSQL در چابکان.نت
2. تنظیم اطلاعات اتصال در `.env`
3. اجرای migration ها

### 4. دامنه

1. تنظیم دامنه در پنل چابکان.نت
2. تنظیم `ALLOWED_HOST` در `.env`
3. تنظیم SSL (اختیاری)

## 🔧 عیب‌یابی

### مشکلات رایج

#### 1. خطای دیتابیس
```bash
# بررسی اتصال
python manage.py dbshell

# اجرای migration
python manage.py migrate
```

#### 2. خطای Static Files
```bash
# جمع‌آوری مجدد
python manage.py collectstatic --clear --noinput
```

#### 3. خطای امنیت
```bash
# بررسی تنظیمات
python security_check.py
```

### لاگ‌ها

```bash
# مشاهده لاگ‌های Django
tail -f logs/django.log

# مشاهده لاگ‌های Gunicorn
# (در console output)
```

## 📞 پشتیبانی

### منابع مفید

- [مستندات چابکان.نت](https://docs.chabokan.net/simple-hosting/django/)
- [مستندات Django](https://docs.djangoproject.com/)
- [مستندات Gunicorn](https://docs.gunicorn.org/)

### تماس با پشتیبانی

- **چابکان.نت**: از طریق پنل کاربری
- **Django**: [Django Forum](https://forum.djangoproject.com/)

## ✅ چک‌لیست استقرار

- [ ] حساب کاربری چابکان.نت ایجاد شده
- [ ] دیتابیس PostgreSQL ایجاد شده
- [ ] فایل `.env` تنظیم شده
- [ ] کد آپلود شده
- [ ] Migration ها اجرا شده
- [ ] Static files جمع‌آوری شده
- [ ] دامنه تنظیم شده
- [ ] SSL فعال شده (اختیاری)
- [ ] تست کامل انجام شده

---

**نکته**: این برنچ مخصوص چابکان.نت است. برای development از برنچ `master` استفاده کنید.

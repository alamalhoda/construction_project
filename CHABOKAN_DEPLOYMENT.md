# راهنمای استقرار پروژه روی چابکان.نت

این راهنما شامل تمام مراحل لازم برای استقرار پروژه Django شما روی سرویس میزبانی چابکان.نت است.

## 📋 فهرست مطالب

1. [پیش‌نیازها](#پیش‌نیازها)
2. [آماده‌سازی پروژه](#آماده‌سازی-پروژه)
3. [تنظیمات چابکان.نت](#تنظیمات-چابکاننت)
4. [استقرار](#استقرار)
5. [تنظیمات امنیتی](#تنظیمات-امنیتی)
6. [عیب‌یابی](#عیب‌یابی)
7. [نگهداری](#نگهداری)

## 🔧 پیش‌نیازها

### 1. حساب کاربری چابکان.نت
- ثبت‌نام در [چابکان.نت](https://chabokan.net)
- ایجاد پروژه جدید Django
- دسترسی به پنل مدیریت

### 2. دیتابیس PostgreSQL
- ایجاد دیتابیس PostgreSQL در چابکان.نت
- دریافت اطلاعات اتصال (نام دیتابیس، کاربر، رمز عبور، هاست، پورت)

### 3. دامنه (اختیاری)
- اگر دامنه سفارشی دارید، آن را در پنل چابکان.نت تنظیم کنید

## 🚀 آماده‌سازی پروژه

### 1. نصب وابستگی‌ها

```bash
# نصب requirements مخصوص چابکان
pip install -r requirements-chabokan.txt
```

### 2. تنظیم متغیرهای محیطی

فایل `.env.chabokan` را کپی کرده و به `.env` تغییر نام دهید:

```bash
cp .env.chabokan .env
```

سپس مقادیر زیر را در فایل `.env` تنظیم کنید:

```env
# Django settings
DEBUG=False
SECRET_KEY=your-secret-key-here
DJANGO_ENVIRONMENT=production

# Database settings (از پنل چابکان.نت دریافت کنید)
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=5432

# Domain settings
ALLOWED_HOST=your-domain.chabokan.net
TRUSTED_ORIGIN=https://your-domain.chabokan.net

# Email settings (اختیاری)
EMAIL_HOST=smtp.chabokan.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@chabokan.net
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@your-domain.chabokan.net
```

### 3. اجرای اسکریپت استقرار

```bash
# اجرای اسکریپت خودکار استقرار
./deploy_chabokan.sh
```

یا به صورت دستی:

```bash
# تنظیم متغیر محیطی
export DJANGO_SETTINGS_MODULE=construction_project.settings_chabokan

# اجرای migration ها
python manage.py migrate

# ایجاد superuser
python manage.py createsuperuser

# جمع‌آوری static files
python manage.py collectstatic --noinput

# بررسی امنیت
python security_chabokan.py
```

## 🌐 تنظیمات چابکان.نت

### 1. آپلود کد

کد پروژه خود را به سرور چابکان.نت آپلود کنید. می‌توانید از Git استفاده کنید:

```bash
# در پنل چابکان.نت، Git repository خود را تنظیم کنید
git remote add chabokan https://git.chabokan.net/your-username/your-repo.git
git push chabokan main
```

### 2. تنظیمات سرور

در پنل چابکان.نت:

1. **Python Version**: Python 3.11 یا بالاتر
2. **WSGI File**: `wsgi_chabokan.py`
3. **Requirements File**: `requirements-chabokan.txt`
4. **Static Files**: `/staticfiles/`
5. **Media Files**: `/media/`

### 3. تنظیمات دیتابیس

1. در پنل چابکان.نت، دیتابیس PostgreSQL ایجاد کنید
2. اطلاعات اتصال را در فایل `.env` قرار دهید
3. Migration ها را اجرا کنید

### 4. تنظیمات Nginx

فایل `nginx_chabokan.conf` را در پنل چابکان.نت آپلود کنید و تنظیمات زیر را اعمال کنید:

- دامنه خود را در `server_name` قرار دهید
- مسیر static files را بررسی کنید
- SSL certificate را تنظیم کنید (اگر دارید)

## 🔒 تنظیمات امنیتی

### 1. بررسی امنیت

```bash
# اجرای بررسی امنیت
python security_chabokan.py
```

### 2. تنظیمات مهم امنیتی

- `DEBUG=False` در production
- `SECRET_KEY` منحصر به فرد
- `ALLOWED_HOSTS` محدود به دامنه شما
- SSL/HTTPS فعال
- HSTS headers تنظیم شده

### 3. فایروال و دسترسی

- پورت‌های غیرضروری را ببندید
- دسترسی SSH را محدود کنید
- لاگ‌های امنیتی را فعال کنید

## 🚀 استقرار

### 1. شروع سرور

```bash
# با Gunicorn
gunicorn --config gunicorn.conf.py wsgi_chabokan:application

# یا با دستور چابکان.نت
python manage.py runserver 0.0.0.0:8000
```

### 2. بررسی عملکرد

```bash
# بررسی وضعیت سرور
curl http://your-domain.chabokan.net/health/

# بررسی static files
curl http://your-domain.chabokan.net/static/admin/css/base.css
```

### 3. تست کامل

1. بازدید از صفحه اصلی
2. تست ورود به پنل ادمین
3. بررسی عملکرد API
4. تست آپلود فایل (اگر دارید)

## 🔧 عیب‌یابی

### مشکلات رایج

#### 1. خطای دیتابیس
```bash
# بررسی اتصال دیتابیس
python manage.py dbshell

# اجرای migration ها
python manage.py migrate --run-syncdb
```

#### 2. خطای Static Files
```bash
# جمع‌آوری مجدد static files
python manage.py collectstatic --clear --noinput

# بررسی مسیر static files
ls -la staticfiles/
```

#### 3. خطای امنیت
```bash
# بررسی تنظیمات امنیت
python security_chabokan.py

# بررسی متغیرهای محیطی
env | grep DJANGO
```

### لاگ‌ها

```bash
# مشاهده لاگ‌های Django
tail -f logs/django.log

# مشاهده لاگ‌های Gunicorn
tail -f logs/gunicorn.log

# مشاهده لاگ‌های Nginx
tail -f /var/log/nginx/error.log
```

## 📊 نگهداری

### 1. پشتیبان‌گیری منظم

```bash
# پشتیبان‌گیری از دیتابیس
python manage.py dumpdata > backup_$(date +%Y%m%d).json

# پشتیبان‌گیری از media files
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

### 2. به‌روزرسانی

```bash
# به‌روزرسانی وابستگی‌ها
pip install -r requirements-chabokan.txt --upgrade

# اجرای migration های جدید
python manage.py migrate

# جمع‌آوری static files
python manage.py collectstatic --noinput
```

### 3. نظارت

- نظارت بر استفاده از CPU و RAM
- بررسی لاگ‌های خطا
- نظارت بر امنیت
- بررسی عملکرد دیتابیس

## 📞 پشتیبانی

### منابع مفید

1. [مستندات چابکان.نت](https://docs.chabokan.net/simple-hosting/django/)
2. [مستندات Django](https://docs.djangoproject.com/)
3. [مستندات Gunicorn](https://docs.gunicorn.org/)

### تماس با پشتیبانی

- پشتیبانی چابکان.نت: از طریق پنل کاربری
- انجمن Django: [Django Forum](https://forum.djangoproject.com/)

## ✅ چک‌لیست نهایی

- [ ] حساب کاربری چابکان.نت ایجاد شده
- [ ] دیتابیس PostgreSQL تنظیم شده
- [ ] متغیرهای محیطی تنظیم شده
- [ ] کد پروژه آپلود شده
- [ ] Migration ها اجرا شده
- [ ] Static files جمع‌آوری شده
- [ ] تنظیمات امنیتی اعمال شده
- [ ] دامنه تنظیم شده
- [ ] SSL فعال شده (اختیاری)
- [ ] تست کامل انجام شده

---

**نکته مهم**: این راهنما بر اساس مستندات چابکان.نت تهیه شده است. در صورت تغییر در سرویس‌های چابکان.نت، این راهنما ممکن است نیاز به به‌روزرسانی داشته باشد.

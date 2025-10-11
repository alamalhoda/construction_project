# راهنمای استقرار (Deployment Guide)

## 🔧 تنظیمات محیط Development vs Production

### محیط Development (توسعه)
```bash
# اجرا با تنظیمات development
python manage.py runserver

# ویژگی‌ها:
✅ همه API ها بدون احراز هویت کار می‌کنند
✅ DEBUG = True
✅ لاگ‌های تفصیلی
✅ Hot reload فعال
```

### محیط Production (اجرا)
```bash
# اجرا با تنظیمات production
python manage.py runserver --settings=construction_project.production_settings

# ویژگی‌ها:
🔒 همه API ها نیاز به احراز هویت دارند
🔒 DEBUG = False
🔒 SSL اجباری
🔒 امنیت کامل
```

## 🚀 مراحل استقرار

### 1. نصب وابستگی‌ها
```bash
pip install -r requirements.txt
pip install gunicorn psycopg2-binary redis django-redis
```

### 2. تنظیم دیتابیس
```bash
# PostgreSQL
sudo -u postgres createdb construction_db
sudo -u postgres createuser construction_user
sudo -u postgres psql -c "ALTER USER construction_user PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE construction_db TO construction_user;"
```

### 3. تنظیم Redis
```bash
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### 4. اجرای Migration
```bash
python manage.py migrate --settings=construction_project.production_settings
python manage.py collectstatic --settings=construction_project.production_settings
```

### 5. ایجاد Superuser
```bash
python manage.py createsuperuser --settings=construction_project.production_settings
```

### 6. اجرا با Gunicorn
```bash
gunicorn --bind 0.0.0.0:8000 construction_project.wsgi:application --settings=construction_project.production_settings
```

## 🔐 امنیت API

### Development Mode
- **همه درخواست‌ها** (GET, POST, PUT, DELETE) بدون احراز هویت
- مناسب برای تست و توسعه
- لاگ‌های تفصیلی

### Production Mode
- **همه درخواست‌ها** نیاز به احراز هویت دارند
- SSL اجباری
- Rate limiting
- Audit logging

## 📝 تست API

### Development
```bash
# بدون احراز هویت
curl http://localhost:8000/api/v1/Transaction/
curl -X POST -H "Content-Type: application/json" -d '{"name":"test"}' http://localhost:8000/api/v1/Project/
```

### Production
```bash
# با احراز هویت
curl -b cookies.txt http://your-domain.com/api/v1/Transaction/
curl -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"name":"test"}' http://your-domain.com/api/v1/Project/
```

## 🛡️ نکات امنیتی

1. **هرگز** `DEBUG = True` در production استفاده نکنید
2. **همیشه** از HTTPS در production استفاده کنید
3. **رمزهای عبور** قوی برای دیتابیس و کاربران استفاده کنید
4. **فایروال** مناسب تنظیم کنید
5. **بک‌آپ** منظم از دیتابیس بگیرید

## 📊 مانیتورینگ

### لاگ‌های امنیتی
```bash
tail -f /var/log/construction/security.log
```

### لاگ‌های عمومی
```bash
tail -f /var/log/construction/django.log
```

## 🔄 به‌روزرسانی

```bash
# 1. بک‌آپ دیتابیس
pg_dump construction_db > backup_$(date +%Y%m%d).sql

# 2. به‌روزرسانی کد
git pull origin main

# 3. Migration
python manage.py migrate --settings=construction_project.production_settings

# 4. جمع‌آوری فایل‌های استاتیک
python manage.py collectstatic --settings=construction_project.production_settings

# 5. راه‌اندازی مجدد
sudo systemctl restart gunicorn
```

# راهنمای Deploy روی Render

## مراحل Deploy

### 1. آماده‌سازی پروژه
پروژه قبلاً برای Render آماده شده و شامل موارد زیر است:
- ✅ Dockerfile بهینه‌شده
- ✅ requirements.txt با PostgreSQL
- ✅ production_settings.py برای Render
- ✅ render.yaml configuration

### 2. ایجاد حساب کاربری Render
1. به [render.com](https://render.com) بروید
2. حساب کاربری ایجاد کنید
3. GitHub account را متصل کنید

### 3. Deploy پروژه
1. **New Web Service** را انتخاب کنید
2. **Build and deploy from a Git repository** را انتخاب کنید
3. Repository را انتخاب کنید
4. تنظیمات زیر را وارد کنید:
   - **Name**: construction-project
   - **Environment**: Docker
   - **Dockerfile Path**: ./Dockerfile
   - **Build Command**: (خالی بگذارید)
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 3 construction_project.wsgi:application`

### 4. ایجاد دیتابیس PostgreSQL
1. **New PostgreSQL** را انتخاب کنید
2. تنظیمات:
   - **Name**: construction-db
   - **Database**: construction_db
   - **User**: construction_user
   - **Plan**: Free

### 5. تنظیم Environment Variables
در بخش Environment Variables:
```
DJANGO_SETTINGS_MODULE=construction_project.production_settings
DB_NAME=construction_db
DB_USER=construction_user
DB_PASSWORD=[از دیتابیس کپی کنید]
DB_HOST=[از دیتابیس کپی کنید]
DB_PORT=5432
SECRET_KEY=[یک کلید امنیتی تولید کنید]
```

### 6. Deploy
1. **Create Web Service** را کلیک کنید
2. منتظر بمانید تا build کامل شود
3. URL نهایی را دریافت کنید

### 7. تنظیم دیتابیس
بعد از deploy موفق:
1. به URL + `/admin/` بروید
2. اگر دیتابیس خالی است، migrations را اجرا کنید
3. Superuser ایجاد کنید

## نکات مهم
- ✅ پروژه از PostgreSQL استفاده می‌کند
- ✅ Static files خودکار collect می‌شوند
- ✅ HTTPS خودکار فعال است
- ✅ Logs در console نمایش داده می‌شوند

## Troubleshooting
- اگر build fail شد، logs را بررسی کنید
- اگر دیتابیس connect نشد، environment variables را چک کنید
- اگر static files نمایش داده نمی‌شوند، collectstatic را اجرا کنید

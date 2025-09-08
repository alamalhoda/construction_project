# راهنمای سریع استقرار در چابکان.نت

## 🚀 مراحل سریع

### 1. آپلود کد
```bash
git clone <your-repo>
cd construction_project
git checkout chabokan-deployment
```

### 2. نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### 3. تنظیم متغیرهای محیطی
فایل `.env` را ویرایش کنید:
```env
DEBUG=False
SECRET_KEY=your-secret-key-here
DB_NAME=your-database-name
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_HOST=your-database-host
ALLOWED_HOST=your-domain.chabokan.net
```

### 4. اجرای migration ها
```bash
python manage.py migrate
```

### 5. جمع‌آوری static files
```bash
python manage.py collectstatic --noinput
```

### 6. شروع سرور

#### گزینه 1: استفاده از اسکریپت
```bash
./start.sh
```

#### گزینه 2: استفاده از Gunicorn مستقیم
```bash
./run_gunicorn.sh
```

#### گزینه 3: دستور مستقیم
```bash
gunicorn construction_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

## 🔧 تنظیمات چابکان.نت

### در پنل چابکان.نت:
1. **Python Version**: 3.11
2. **WSGI Module**: `construction_project.wsgi:application`
3. **Requirements File**: `requirements.txt`
4. **Static Files**: `/staticfiles/`
5. **Start Command**: `./start.sh` یا `gunicorn construction_project.wsgi:application`

## 🔍 بررسی وضعیت

### Health Check
```bash
curl http://your-domain.chabokan.net/health/simple/
# باید {"status": "OK"} برگرداند
```

### بررسی امنیت
```bash
python security_check.py
```

## ⚠️ مشکلات رایج

### 1. خطای "No application module specified"
**راه حل**: از دستور کامل استفاده کنید:
```bash
gunicorn construction_project.wsgi:application
```

### 2. خطای دیتابیس
**راه حل**: 
- بررسی اطلاعات دیتابیس در `.env`
- اجرای `python manage.py migrate`

### 3. خطای Static Files
**راه حل**:
```bash
python manage.py collectstatic --clear --noinput
```

## 📞 پشتیبانی

- **مستندات چابکان**: [docs.chabokan.net](https://docs.chabokan.net/simple-hosting/django/)
- **لاگ‌ها**: در console output چابکان.نت
- **Health Check**: `/health/` برای بررسی وضعیت

---

**نکته**: اگر مشکلی داشتید، ابتدا `python security_check.py` را اجرا کنید تا وضعیت سیستم را بررسی کنید.

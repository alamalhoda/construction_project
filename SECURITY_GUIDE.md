# 🛡️ راهنمای امنیتی پروژه ساختمانی

## 📋 فهرست مطالب

1. [بررسی امنیتی](#بررسی-امنیتی)
2. [تنظیمات امنیتی](#تنظیمات-امنیتی)
3. [احراز هویت](#احراز-هویت)
4. [نظارت امنیتی](#نظارت-امنیتی)
5. [محافظت از داده‌ها](#محافظت-از-دادهها)
6. [دستورات امنیتی](#دستورات-امنیتی)
7. [بهترین روش‌ها](#بهترین-روشها)

## 🔍 بررسی امنیتی

### اجرای بررسی امنیتی

```bash
# بررسی کامل امنیتی
python manage.py security_check

# بررسی تنظیمات
python manage.py security_check --check-type settings

# بررسی داده‌ها
python manage.py security_check --check-type data --fix-issues

# پاک کردن داده‌های قدیمی
python manage.py security_check --check-type cleanup
```

### بررسی دستی

```bash
# اجرای اسکریپت بررسی امنیتی
python security_audit.py
```

## ⚙️ تنظیمات امنیتی

### تنظیمات Development

```python
# در settings.py
ENVIRONMENT = 'development'
```

### تنظیمات Production

```python
# در settings.py
ENVIRONMENT = 'production'
```

### متغیرهای محیطی

```bash
# تنظیم متغیرهای محیطی
export DJANGO_ENVIRONMENT=production
export SECRET_KEY=your-secret-key-here
export DB_PASSWORD=your-db-password
export EMAIL_HOST_PASSWORD=your-email-password
```

## 🔐 احراز هویت

### ویژگی‌های امنیتی

- ✅ **قفل شدن حساب**: پس از 5 تلاش ناموفق
- ✅ **رمز عبور قوی**: حداقل 12 کاراکتر
- ✅ **جلسات امن**: بررسی IP و User Agent
- ✅ **احراز هویت دو مرحله‌ای**: پشتیبانی از 2FA

### تنظیم رمز عبور قوی

```python
from construction.authentication import PasswordSecurity

# بررسی قدرت رمز عبور
errors = PasswordSecurity.validate_password_strength("password123")
if errors:
    print("مشکلات رمز عبور:", errors)

# تولید رمز عبور امن
secure_password = PasswordSecurity.generate_secure_password()
```

### احراز هویت دو مرحله‌ای

```python
from construction.authentication import TwoFactorAuthentication

# تولید کلید مخفی
secret = TwoFactorAuthentication.generate_secret()

# تولید کدهای پشتیبان
backup_codes = TwoFactorAuthentication.generate_backup_codes()

# بررسی کد TOTP
is_valid = TwoFactorAuthentication.verify_totp_code(secret, "123456")
```

## 👁️ نظارت امنیتی

### رویدادهای امنیتی

```python
from construction.security_monitoring import SecurityMonitor

# ثبت رویداد امنیتی
SecurityMonitor.log_event(
    event_type='login_failed',
    severity='medium',
    user=user,
    request=request,
    description='تلاش ورود ناموفق'
)

# تحلیل فعالیت‌های مشکوک
SecurityMonitor.analyze_suspicious_activity()

# دریافت آمار داشبورد
dashboard_data = SecurityMonitor.get_security_dashboard_data()
```

### گزارش‌های امنیتی

```python
from construction.security_monitoring import SecurityReport

# گزارش روزانه
daily_report = SecurityReport.generate_daily_report()

# گزارش هفتگی
weekly_report = SecurityReport.generate_weekly_report()
```

## 🗄️ محافظت از داده‌ها

### رمزگذاری داده‌ها

```python
from construction.data_protection import DataEncryption

# رمزگذاری داده حساس
encrypted_data = DataEncryption.encrypt_sensitive_data("sensitive data")

# هش کردن رمز عبور
password_hash, salt = DataEncryption.hash_password("password123")
```

### ناشناس‌سازی داده‌ها

```python
from construction.data_protection import DataAnonymization

# ناشناس‌سازی کاربر
DataAnonymization.anonymize_user_data(user)

# ناشناس‌سازی فیلدهای حساس
DataAnonymization.anonymize_sensitive_fields(
    model_instance, 
    ['phone', 'email', 'address']
)
```

### پشتیبان‌گیری امن

```python
from construction.data_protection import DataBackup

# ایجاد پشتیبان رمزگذاری شده
backup_file = DataBackup.create_encrypted_backup()
```

### بررسی یکپارچگی داده‌ها

```python
from construction.data_protection import DataIntegrity

# بررسی یکپارچگی
issues = DataIntegrity.verify_data_integrity()

# رفع مشکلات
fixed_count = DataIntegrity.fix_integrity_issues(issues)
```

## 🛠️ دستورات امنیتی

### دستورات Django

```bash
# بررسی امنیتی
python manage.py security_check

# ایجاد superuser
python manage.py createsuperuser

# جمع‌آوری فایل‌های استاتیک
python manage.py collectstatic

# اجرای migrations
python manage.py migrate
```

### دستورات سیستم

```bash
# بررسی مجوزهای فایل‌ها
ls -la db.sqlite3
ls -la construction_project/settings.py

# تنظیم مجوزهای امن
chmod 600 db.sqlite3
chmod 600 construction_project/settings.py
chmod 700 logs/
```

## 📚 بهترین روش‌ها

### 1. تنظیمات Production

- ✅ `DEBUG = False`
- ✅ `ALLOWED_HOSTS` تنظیم شده
- ✅ `SECRET_KEY` قوی و مخفی
- ✅ HTTPS فعال
- ✅ Database امن (PostgreSQL)

### 2. احراز هویت

- ✅ رمز عبور قوی (12+ کاراکتر)
- ✅ قفل شدن حساب
- ✅ جلسات امن
- ✅ احراز هویت دو مرحله‌ای

### 3. نظارت

- ✅ ثبت رویدادهای امنیتی
- ✅ تحلیل فعالیت‌های مشکوک
- ✅ گزارش‌های منظم
- ✅ هشدارهای فوری

### 4. محافظت از داده‌ها

- ✅ رمزگذاری داده‌های حساس
- ✅ پشتیبان‌گیری منظم
- ✅ ناشناس‌سازی داده‌ها
- ✅ بررسی یکپارچگی

### 5. نگهداری

- ✅ به‌روزرسانی منظم
- ✅ پاک کردن داده‌های قدیمی
- ✅ بررسی آسیب‌پذیری‌ها
- ✅ تست امنیتی

## 🚨 هشدارهای امنیتی

### موارد خطرناک

- ❌ `DEBUG = True` در production
- ❌ `ALLOWED_HOSTS = []` در production
- ❌ `SECRET_KEY` ضعیف
- ❌ عدم استفاده از HTTPS
- ❌ رمز عبور ضعیف

### اقدامات فوری

1. **تغییر رمز عبور ادمین**
2. **بررسی لاگ‌های امنیتی**
3. **بررسی دسترسی‌های غیرمجاز**
4. **به‌روزرسانی سیستم**

## 📞 تماس اضطراری

در صورت بروز مشکل امنیتی:

1. **قطع دسترسی**: خاموش کردن سرور
2. **بررسی لاگ‌ها**: بررسی فایل‌های لاگ
3. **تغییر رمزها**: تغییر همه رمزهای عبور
4. **گزارش**: گزارش به تیم امنیتی

## 📖 منابع بیشتر

- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

---

**⚠️ توجه**: این راهنما برای پروژه ساختمانی تهیه شده است. برای پروژه‌های دیگر، تنظیمات را بر اساس نیازهای خاص تنظیم کنید.

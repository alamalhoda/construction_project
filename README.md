# سیستم مدیریت پروژه ساخت‌وساز

سیستم جامع مدیریت پروژه‌های ساخت‌وساز با قابلیت‌های مدیریت سرمایه‌گذاران، تراکنش‌ها، واحدها و گزارش‌گیری.

## ✨ ویژگی‌های اصلی

### 🏢 مدیریت پروژه‌ها
- ایجاد و مدیریت پروژه‌های ساخت‌وساز
- تاریخ شروع و پایان (شمسی و میلادی)
- مدیریت واحدهای مسکونی

### 👥 مدیریت سرمایه‌گذاران
- ثبت اطلاعات کامل سرمایه‌گذاران
- ارتباط چندگانه با واحدها
- پروفایل مالی و گزارش‌گیری

### 💰 مدیریت تراکنش‌ها
- ثبت تراکنش‌های مختلف (آورده، خروج، سود)
- تاریخ‌گذاری شمسی
- گزارش‌گیری مالی

### 📊 داشبورد و گزارش‌ها
- داشبورد جامع با آمار کلی
- گزارش‌های مالی و تحلیلی
- نمودارها و نمایش داده‌ها
- **خروجی Excel Dynamic** با فرمول‌های محاسباتی ⭐

### 🔐 امنیت و احراز هویت
- سیستم لاگین و ثبت نام
- کنترل دسترسی بر اساس نقش‌ها
- امنیت بالا با محافظت‌های مختلف

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها
- Python 3.8+
- Django 4.1+
- SQLite (پیش‌فرض) یا PostgreSQL

### نصب
```bash
# کلون کردن پروژه
git clone <repository-url>
cd construction_project

# ایجاد محیط مجازی
python -m venv env
source env/bin/activate  # Linux/Mac
# یا
env\Scripts\activate  # Windows

# نصب وابستگی‌ها
pip install -r requirements.txt

# اجرای migrations
python manage.py migrate

# ایجاد superuser
python manage.py createsuperuser

# اجرای سرور
python manage.py runserver
```

## 🌐 آدرس‌های مهم

### 📊 داشبورد اصلی
```
http://localhost:8000/dashboard/
```

### 🔐 احراز هویت
```
http://localhost:8000/construction/login/     - ورود به سیستم
http://localhost:8000/construction/register/  - ثبت نام
```

### ⚙️ پنل ادمین
```
http://localhost:8000/admin/
```

## 👥 کاربران تست

### 🔧 مدیر فنی
```
نام کاربری: admin
رمز عبور: admin123
دسترسی: Django Admin + همه چیز
```

### 👤 کاربر نهایی
```
نام کاربری: user1
رمز عبور: user123
دسترسی: فقط داشبورد و صفحات مجاز
```

## 📋 صفحات مجاز برای کاربران نهایی

```
http://localhost:8000/dashboard/project/           - مشاهده پروژه‌ها
http://localhost:8000/dashboard/transaction-manager/ - مدیریت تراکنش‌ها
http://localhost:8000/dashboard/investor-profile/   - پروفایل سرمایه‌گذاران
```

## 🛡️ امنیت

### ویژگی‌های امنیتی فعال:
- ✅ احراز هویت اجباری
- ✅ محافظت CSRF
- ✅ Session Management
- ✅ Password Validation
- ✅ Audit Logging
- ✅ Account Lockout (5 تلاش ناموفق)

### محافظت از صفحات:
- **صفحات محافظت شده**: `/construction/`, `/dashboard/`
- **صفحات عمومی**: `/`, `/login/`, `/register/`, `/admin/`

## 📁 ساختار پروژه

```
construction_project/
├── 📄 README.md                    # راهنمای کامل پروژه
├── 📄 requirements.txt             # وابستگی‌های Python
├── 📄 project_requirements.rtl.txt # نیازمندی‌های پروژه
├── 📄 pytest.ini                  # تنظیمات تست
├── 📄 manage.py                    # مدیریت Django
├── 📄 db.sqlite3                   # دیتابیس
├── 🏢 construction/               # اپلیکیشن اصلی
├── 📊 dashboard/                   # اپلیکیشن داشبورد
├── 💾 backup/                      # اپلیکیشن پشتیبان‌گیری
├── ⚙️ construction_project/        # تنظیمات پروژه
├── 📁 templates/                   # قالب‌های HTML
├── 📁 staticfiles/                 # فایل‌های استاتیک
├── 📁 tests/                       # تست‌ها
├── 📁 scripts/                     # اسکریپت‌های کمکی
├── 📁 backups/                     # فایل‌های پشتیبان
├── 📁 logs/                        # فایل‌های لاگ
├── 📁 temp_data/                   # داده‌های موقت
└── 📁 docs/                        # مستندات و راهنماها
    ├── 📁 guides/                  # راهنماهای کاربری
    ├── 📁 security/                # مستندات امنیتی
    └── 📁 tests/                   # فایل‌های تست
```

## 📚 مستندات

### 📖 راهنماهای کاربری
- `docs/guides/` - راهنماهای کامل استفاده از سیستم
- `docs/security/` - مستندات امنیتی
- `docs/tests/` - فایل‌های تست و کمکی

### 🔧 مدیریت داده‌ها

#### مدل‌های اصلی:
- **Project**: پروژه‌های ساخت‌وساز
- **Unit**: واحدهای مسکونی
- **Investor**: سرمایه‌گذاران
- **Transaction**: تراکنش‌ها
- **Period**: دوره‌های زمانی
- **Expense**: هزینه‌ها
- **InterestRate**: نرخ‌های بهره

#### API Endpoints:
```
GET  /api/projects/           - لیست پروژه‌ها
POST /api/projects/           - ایجاد پروژه جدید
GET  /api/investors/          - لیست سرمایه‌گذاران
POST /api/investors/          - ایجاد سرمایه‌گذار جدید
GET  /api/transactions/       - لیست تراکنش‌ها
POST /api/transactions/       - ایجاد تراکنش جدید
```

## 📊 پشتیبان‌گیری

### پشتیبان‌گیری خودکار:
```bash
# تنظیم cron job
python scripts/setup_cron.sh

# اجرای دستی پشتیبان‌گیری
python scripts/create_backup.py

# لیست پشتیبان‌ها
python scripts/list_backups.py

# بازیابی پشتیبان
python scripts/restore_backup.py
```

## 🧪 تست

### اجرای تست‌ها:
```bash
# تست‌های کامل
python manage.py test

# تست‌های خاص
python manage.py test construction.tests.test_models
python manage.py test construction.tests.test_views
```

## 🚀 استقرار (Deployment)

### تنظیمات Production:
```bash
# تنظیم متغیر محیطی
export DJANGO_ENVIRONMENT=production

# اجرای با تنظیمات production
python manage.py runserver --settings=construction_project.production_settings
```

### تنظیمات امنیتی Production:
- SSL/HTTPS اجباری
- تنظیمات دیتابیس PostgreSQL
- Cache با Redis
- Logging پیشرفته
- Rate Limiting

## 🤝 مشارکت

1. Fork کنید
2. Branch جدید ایجاد کنید (`git checkout -b feature/amazing-feature`)
3. تغییرات را commit کنید (`git commit -m 'Add amazing feature'`)
4. Branch را push کنید (`git push origin feature/amazing-feature`)
5. Pull Request ایجاد کنید

## 📚 مستندات

### مستندات اصلی
- [📖 راهنمای API](docs/API_REFERENCE.md) - مستندات کامل API
- [📊 Excel Dynamic](DYNAMIC_EXCEL_DOCUMENTATION.md) - مستندات کامل Excel با فرمول
- [⚡ مرجع سریع Dynamic](DYNAMIC_EXCEL_QUICK_REFERENCE.md) - راهنمای سریع Excel Dynamic
- [📄 Excel Static](STATIC_EXCEL_DOCUMENTATION.md) - مستندات کامل Excel گزارش‌گیری
- [🚀 مرجع سریع Static](STATIC_EXCEL_QUICK_REFERENCE.md) - راهنمای سریع Excel Static
- [💾 مدیریت دیتابیس](DATABASE_MANAGEMENT.md) - راهنمای مدیریت دیتابیس
- [🔄 تبدیل ریال به تومان](RIAL_TO_TOMAN_CONVERSION.md) - راهنمای تبدیل واحد پول

### مستندات توسعه
- [🐳 Docker](DOCKER_README.md) - راهنمای استفاده از Docker
- [🚀 Deploy](DEPLOY_README.md) - راهنمای استقرار
- [📝 Django Scripts](DJANGO_SCRIPTS.md) - راهنمای اسکریپت‌های Django

### ویژگی‌های خاص

#### Excel Dynamic (فرمول‌محور)
- 29 Named Range
- 18 شیت مختلف
- محاسبات زنجیره‌ای
- محاسبه سود تراکنش‌ها
- دوره متوسط ساخت
- قابلیت ویرایش و تحلیل

#### Excel Static (گزارش‌محور)
- 15 شیت مختلف
- محاسبات سرور
- رنگ‌بندی استاندارد
- شاخص نفع سرمایه‌گذاران
- خلاصه دوره‌ای
- آماده چاپ و ارائه

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است.

## 📞 پشتیبانی

برای سوالات و پشتیبانی، لطفاً issue ایجاد کنید یا با تیم توسعه تماس بگیرید.

---

**🎉 سیستم مدیریت پروژه ساخت‌وساز آماده استفاده است!**

# 🎯 راهنمای سیستم نقش‌های کاربری

## ✅ سیستم نقش‌های کاربری پیاده‌سازی شد

### 🔧 **مدیر فنی** (شما)
- **دسترسی کامل** به همه بخش‌های سیستم
- **مدیریت پروژه‌ها** - ایجاد، ویرایش، حذف
- **مدیریت سرمایه‌گذاران** - ایجاد، ویرایش، حذف
- **مدیریت تراکنش‌ها** - ایجاد، ویرایش، حذف
- **مدیریت واحدها** - ایجاد، ویرایش، حذف
- **دسترسی به پنل ادمین** - مدیریت کامل سیستم
- **دسترسی به HTMX** - رابط کاربری پیشرفته
- **گزارش‌ها و آمار** - مشاهده تمام گزارش‌ها

### 👤 **کاربر نهایی/بهره‌بردار**
- **دسترسی محدود** به بخش‌های خاص
- **مشاهده پروژه‌ها** - فقط مشاهده (بدون ویرایش)
- **مشاهده سرمایه‌گذاران** - فقط مشاهده (بدون ویرایش)
- **مشاهده تراکنش‌ها** - فقط مشاهده (بدون ویرایش)
- **گزارش‌ها و آمار** - مشاهده گزارش‌های عمومی
- **دسترسی به داشبورد** - داشبورد شخصی

## 🌐 آدرس‌های مهم

### 📊 **داشبورد اصلی** (آدرس مورد نظر شما)
```
http://localhost:8000/dashboard/
```
- **آمار کلی سیستم** - تعداد پروژه‌ها، سرمایه‌گذاران، تراکنش‌ها
- **آخرین فعالیت‌ها** - پروژه‌ها، تراکنش‌ها، سرمایه‌گذاران
- **عملیات سریع** - دسترسی سریع به بخش‌های مختلف
- **کنترل دسترسی** - نمایش محتوا بر اساس نقش کاربر

### 👤 **داشبورد کاربری**
```
http://localhost:8000/construction/user-dashboard/
```
- **داشبورد شخصی** - اطلاعات کاربر و دسترسی‌ها
- **عملیات کاربری** - پروفایل، تغییر رمز عبور
- **لینک به داشبورد اصلی** - دسترسی به داشبورد اصلی

### 🔐 **صفحات احراز هویت**
```
http://localhost:8000/construction/login/     - ورود به سیستم
http://localhost:8000/construction/register/  - ثبت نام
```

## 👥 کاربران تست

### 🔧 **مدیر فنی**
```
نام کاربری: admin
رمز عبور: admin123
نقش: مدیر فنی
دسترسی: کامل
```

### 👤 **کاربر نهایی**
```
نام کاربری: testuser
رمز عبور: testpass123
نقش: کاربر نهایی/بهره‌بردار
دسترسی: محدود
```

## 🛡️ کنترل دسترسی

### ✅ **Decorator های امنیتی**
- `@technical_admin_required` - فقط مدیر فنی
- `@end_user_required` - فقط کاربر نهایی
- `@dashboard_access_required` - دسترسی به داشبورد
- `@role_required('technical_admin')` - نقش خاص

### 🔒 **محافظت از صفحات**
- **صفحات محافظت شده** - نیاز به ورود
- **کنترل نقش** - بررسی نقش کاربر
- **هدایت خودکار** - هدایت به صفحه مناسب

## 📁 فایل‌های ایجاد شده

### 🗃️ **مدل‌ها**
- `construction/models.py` - مدل `UserProfile` اضافه شد
- `construction/admin.py` - ثبت مدل در ادمین

### 🎭 **Decorator ها**
- `construction/decorators.py` - کنترل دسترسی

### 🔗 **Signal ها**
- `construction/signals.py` - ایجاد خودکار پروفایل
- `construction/apps.py` - فعال‌سازی signal ها

### 📊 **View ها**
- `construction/dashboard_views.py` - داشبورد اصلی
- `construction/user_views.py` - به‌روزرسانی شده

### 🎨 **Template ها**
- `construction/templates/construction/main_dashboard.html` - داشبورد اصلی
- `construction/templates/construction/user_dashboard.html` - به‌روزرسانی شده

### 🔗 **URL ها**
- `construction/urls.py` - URL های جدید اضافه شد

## 🧪 نحوه تست

### 1. **تست مدیر فنی**
```bash
# ورود با مدیر فنی
نام کاربری: admin
رمز عبور: admin123

# بررسی دسترسی‌ها
- داشبورد اصلی: http://localhost:8000/dashboard/
- پنل ادمین: http://localhost:8000/admin/
- مدیریت پروژه‌ها: http://localhost:8000/construction/Project/
- HTMX: http://localhost:8000/construction/protected/htmx/
```

### 2. **تست کاربر نهایی**
```bash
# ورود با کاربر نهایی
نام کاربری: testuser
رمز عبور: testpass123

# بررسی دسترسی‌ها
- داشبورد اصلی: http://localhost:8000/dashboard/
- مشاهده پروژه‌ها: http://localhost:8000/construction/Project/
- پنل ادمین: ❌ دسترسی ندارد
- HTMX: ❌ دسترسی ندارد
```

### 3. **تست کنترل دسترسی**
```bash
# تست دسترسی بدون ورود
http://localhost:8000/dashboard/ → هدایت به لاگین

# تست دسترسی با نقش اشتباه
کاربر نهایی → HTMX → پیام خطا + هدایت به داشبورد
```

## 🔧 مدیریت کاربران

### 📝 **ایجاد کاربر جدید**
```python
# در Django Shell
from django.contrib.auth.models import User
from construction.models import UserProfile

# ایجاد کاربر
user = User.objects.create_user('username', 'email@example.com', 'password')
user.first_name = 'نام'
user.last_name = 'نام خانوادگی'
user.save()

# تنظیم نقش
profile = user.userprofile
profile.role = 'end_user'  # یا 'technical_admin'
profile.phone = '09123456789'
profile.department = 'بخش'
profile.save()
```

### 🔄 **تغییر نقش کاربر**
```python
# در Django Shell
user = User.objects.get(username='username')
profile = user.userprofile
profile.role = 'technical_admin'  # تغییر نقش
profile.save()
```

### 🗑️ **حذف کاربر**
```python
# در Django Shell
user = User.objects.get(username='username')
user.delete()  # پروفایل هم حذف می‌شود
```

## 📊 ویژگی‌های داشبورد اصلی

### 📈 **آمار کلی**
- تعداد پروژه‌ها
- تعداد سرمایه‌گذاران
- تعداد تراکنش‌ها
- تعداد واحدها
- تعداد هزینه‌ها

### 📋 **آخرین فعالیت‌ها**
- آخرین پروژه‌ها
- آخرین تراکنش‌ها
- آخرین سرمایه‌گذاران

### ⚡ **عملیات سریع**
- دسترسی سریع به بخش‌های مختلف
- دکمه‌های مخصوص هر نقش
- لینک به داشبورد کاربری

## 🎯 خلاصه

### ✅ **کارهای انجام شده:**
1. **سیستم نقش‌ها** - مدیر فنی و کاربر نهایی
2. **کنترل دسترسی** - decorator های امنیتی
3. **داشبورد اصلی** - آدرس `/dashboard/` با آمار کامل
4. **داشبورد کاربری** - داشبورد شخصی
5. **مدیریت کاربران** - ایجاد و مدیریت نقش‌ها
6. **امنیت** - محافظت از صفحات و API ها

### 🌐 **آدرس‌های کلیدی:**
```
داشبورد اصلی: http://localhost:8000/dashboard/
داشبورد کاربری: http://localhost:8000/construction/user-dashboard/
ورود: http://localhost:8000/construction/login/
ثبت نام: http://localhost:8000/construction/register/
```

### 👥 **کاربران تست:**
```
مدیر فنی: admin / admin123
کاربر نهایی: testuser / testpass123
```

---

**🎉 سیستم نقش‌های کاربری کاملاً آماده است!**

**🔧 شما به عنوان مدیر فنی** به همه چیز دسترسی دارید
**👤 کاربران نهایی** فقط به بخش‌های محدود دسترسی دارند
**📊 داشبورد اصلی** در آدرس `/dashboard/` آماده است

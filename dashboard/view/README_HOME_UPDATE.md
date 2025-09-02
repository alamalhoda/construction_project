# به‌روزرسانی صفحه Home - اضافه شدن مدیریت تراکنش‌ها

## تغییرات انجام شده

### 1. اضافه شدن منوی جدید
- **مدیریت تراکنش‌ها** به منوی اصلی اضافه شد
- آیکون 💰 برای تشخیص آسان
- توضیح: "مدیریت کامل تراکنش‌های مالی"

### 2. بهبود ظاهری
- اضافه شدن آیکون‌های مناسب برای تمام منوها:
  - 📊 نمایشگر CSV ساده
  - 📈 نمایشگر CSV پیشرفته  
  - 👥 پروفایل سرمایه‌گذاران
  - 💰 مدیریت تراکنش‌ها

### 3. تنظیمات URL
- URL جدید: `/dashboard/transaction-manager/`
- نام URL: `dashboard:transaction_manager`
- View: `transaction_manager` در `dashboard/views.py`

## فایل‌های تغییر یافته

### 1. `templates/dashboard/home.html`
```html
<!-- منوی جدید اضافه شده -->
<a href="{% url 'dashboard:transaction_manager' %}" class="menu-item">
    <h3>💰 مدیریت تراکنش‌ها</h3>
    <p>مدیریت کامل تراکنش‌های مالی</p>
</a>
```

### 2. `dashboard/urls.py`
```python
# URL جدید اضافه شده
path('transaction-manager/', views.transaction_manager, name='transaction_manager'),
```

### 3. `dashboard/views.py`
```python
# View جدید اضافه شده
def transaction_manager(request):
    """نمایش صفحه مدیریت تراکنش‌های مالی"""
    file_path = os.path.join(settings.BASE_DIR, 'dashboard', 'view', 'transaction_manager.html')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return HttpResponse(content)
    except FileNotFoundError:
        return HttpResponse('فایل یافت نشد', status=404)
```

## نحوه دسترسی

### از طریق مرورگر:
1. به آدرس `/dashboard/` بروید
2. روی "💰 مدیریت تراکنش‌ها" کلیک کنید
3. صفحه مدیریت تراکنش‌ها باز خواهد شد

### از طریق کد:
```python
from django.urls import reverse
from django.shortcuts import redirect

# ریدایرکت به صفحه مدیریت تراکنش‌ها
return redirect('dashboard:transaction_manager')
```

## ویژگی‌های صفحه مدیریت تراکنش‌ها

### 📊 نمایش داده‌ها
- جدول تعاملی با Tabulator
- رنگ‌بندی تراکنش‌ها
- صفحه‌بندی و مرتب‌سازی

### 🔍 فیلترها و جستجو
- فیلتر بر اساس سرمایه‌گذار، پروژه، دوره، نوع تراکنش
- جستجوی متنی در تمام فیلدها

### 📈 آمار و خلاصه
- کارت‌های آماری زیبا
- مجموع واریزها، برداشت‌ها و سودها
- تعداد سرمایه‌گذاران فعال

### ➕ عملیات CRUD
- افزودن تراکنش جدید
- ویرایش تراکنش‌های موجود
- حذف تراکنش با تأیید

### 📤 صادرات
- دانلود CSV
- دانلود JSON

## تست عملکرد

### 1. تست URL
```bash
python manage.py show_urls | grep transaction
```

### 2. تست Django
```bash
python manage.py check
```

### 3. تست دسترسی
- به `/dashboard/` بروید
- روی منوی جدید کلیک کنید
- صفحه باید به درستی بارگذاری شود

## نکات مهم

1. **فایل HTML**: صفحه `transaction_manager.html` باید در پوشه `dashboard/view/` موجود باشد
2. **API**: اطمینان حاصل کنید که API های مربوط به تراکنش‌ها فعال هستند
3. **دسترسی**: صفحه از طریق URL `/dashboard/transaction-manager/` قابل دسترسی است

## عیب‌یابی

### مشکل: صفحه بارگذاری نمی‌شود
- بررسی کنید که فایل `transaction_manager.html` موجود است
- بررسی کنید که URL در `urls.py` درست تنظیم شده است
- بررسی کنید که view در `views.py` درست تعریف شده است

### مشکل: منو نمایش داده نمی‌شود
- بررسی کنید که template درست کامپایل می‌شود
- بررسی کنید که آیکون‌ها در مرورگر نمایش داده می‌شوند

### مشکل: خطای 404
- بررسی کنید که URL pattern درست است
- بررسی کنید که view function درست تعریف شده است
- بررسی کنید که فایل HTML موجود است

# راهنمای استفاده از django-jalali

این پروژه از کتابخانه `django-jalali==7.4.0` برای کار با تاریخ شمسی استفاده می‌کند.

## نصب و تنظیمات

### 1. نصب کتابخانه
```bash
pip install django-jalali==7.4.0
```

### 2. تنظیمات در settings.py

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django_jalali",  # اضافه کردن قبل از اپلیکیشن‌های سفارشی
    'rest_framework',
    'django_htmx',
    'construction',
    'django_extensions',
]

JALALI_SETTINGS = {
    # فایل‌های JavaScript برای ویجت تاریخ شمسی در ادمین
    "ADMIN_JS_STATIC_FILES": [
        "admin/jquery.ui.datepicker.jalali/scripts/jquery-1.10.2.min.js",
        "admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.core.js",
        "admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc.js",
        "admin/jquery.ui.datepicker.jalali/scripts/calendar.js",
        "admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc-fa.js",
        "admin/main.js",
    ],
    # فایل‌های CSS برای ویجت تاریخ شمسی در ادمین
    "ADMIN_CSS_STATIC_FILES": {
        "all": [
            "admin/jquery.ui.datepicker.jalali/themes/base/jquery-ui.min.css",
            "admin/css/main.css",
        ]
    },
}

LANGUAGE_CODE = 'fa-ir'
USE_I18N = True
USE_L10N = True
USE_TZ = True
```

## استفاده در مدل‌ها

### 1. Import کردن jmodels

```python
from django.db import models
from django_jalali.db import models as jmodels

class Project(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام پروژه")
    start_date_shamsi = jmodels.jDateField(verbose_name="تاریخ شروع (شمسی)")
    end_date_shamsi = jmodels.jDateField(verbose_name="تاریخ پایان (شمسی)")
    start_date_gregorian = models.DateField(verbose_name="تاریخ شروع (میلادی)")
    end_date_gregorian = models.DateField(verbose_name="تاریخ پایان (میلادی)")
```

### 2. انواع فیلدهای موجود در django-jalali

- `jDateField`: فیلد تاریخ شمسی
- `jDateTimeField`: فیلد تاریخ و زمان شمسی

## استفاده در فرم‌ها

### 1. Import کردن jDateField

```python
from django import forms
from django_jalali.forms import jDateField
from . import models

class ProjectForm(forms.ModelForm):
    start_date_shamsi = jDateField(label="تاریخ شروع (شمسی)")
    end_date_shamsi = jDateField(label="تاریخ پایان (شمسی)")
    
    class Meta:
        model = models.Project
        fields = [
            "name",
            "start_date_shamsi",
            "end_date_shamsi",
            "start_date_gregorian",
            "end_date_gregorian",
        ]
```

## استفاده در تمپلیت‌ها

### 1. Load کردن jformat

```html
{% load jformat %}
```

### 2. فرمت‌های مختلف نمایش تاریخ

```html
<!-- نمایش کامل تاریخ با نام روز و ماه -->
{{ object.start_date_shamsi|jformat:"%A، %d %B %Y" }}

<!-- نمایش ساده تاریخ -->
{{ object.start_date_shamsi|jformat:"%Y/%m/%d" }}

<!-- نمایش تاریخ و زمان -->
{{ object.created_at|jformat:"%Y/%m/%d - %H:%M" }}
```

### 3. فرمت‌های پشتیبانی شده

- `%Y`: سال چهار رقمی (مثال: ۱۴۰۳)
- `%m`: ماه دو رقمی (مثال: ۰۵)
- `%d`: روز دو رقمی (مثال: ۱۵)
- `%B`: نام کامل ماه (مثال: فروردین)
- `%A`: نام کامل روز هفته (مثال: یکشنبه)
- `%H`: ساعت (۰۰-۲۳)
- `%M`: دقیقه (۰۰-۵۹)

## مثال کاربرد کامل

### models.py
```python
from django.db import models
from django_jalali.db import models as jmodels

class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان رویداد")
    date_shamsi = jmodels.jDateField(verbose_name="تاریخ شمسی")
    date_gregorian = models.DateField(verbose_name="تاریخ میلادی")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "رویداد"
        verbose_name_plural = "رویدادها"

    def __str__(self):
        return self.title
```

### forms.py
```python
from django import forms
from django_jalali.forms import jDateField
from . import models

class EventForm(forms.ModelForm):
    date_shamsi = jDateField(label="تاریخ رویداد")
    
    class Meta:
        model = models.Event
        fields = ['title', 'date_shamsi', 'date_gregorian']
```

### template.html
```html
{% load jformat %}

<div class="event-detail">
    <h2>{{ event.title }}</h2>
    <p>تاریخ رویداد: {{ event.date_shamsi|jformat:"%A، %d %B %Y" }}</p>
    <p>ایجاد شده در: {{ event.created_at|jformat:"%Y/%m/%d در ساعت %H:%M" }}</p>
</div>
```

## مزایای django-jalali

1. **یکپارچگی کامل با Django**: کار با ORM و Admin Django
2. **ویجت‌های آماده**: انتخابگر تاریخ شمسی در ادمین Django
3. **فیلترهای قدرتمند**: jformat برای نمایش زیبای تاریخ‌ها
4. **پشتیبانی کامل**: از تمام عملیات‌های Django روی تاریخ
5. **عملکرد بهتر**: بهینه‌سازی شده برای Django

## نکات مهم

- فیلدهای `jDateField` به صورت خودکار تاریخ شمسی را در دیتابیس ذخیره می‌کنند
- در ادمین Django، ویجت تاریخ شمسی به صورت خودکار نمایش داده می‌شود
- می‌توانید هم تاریخ شمسی و هم میلادی را در یک مدل نگهداری کنید
- برای تبدیل بین تاریخ شمسی و میلادی از توابع داخلی کتابخانه استفاده کنید

## تفاوت با jdatetime

- `jdatetime`: کتابخانه پایه برای کار با تاریخ شمسی در Python
- `django-jalali`: کتابخانه تخصصی برای Django که از jdatetime استفاده می‌کند

django-jalali برای پروژه‌های Django بهتر است چون:
- یکپارچگی کامل با Django داشته
- ویجت‌های آماده ارائه می‌دهد
- ORM Django را پشتیبانی می‌کند

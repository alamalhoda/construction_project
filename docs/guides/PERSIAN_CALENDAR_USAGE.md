# راهنمای استفاده از تقویم شمسی

این پروژه از تقویم شمسی برای نمایش و ورود تاریخ‌ها استفاده می‌کند.

## ویژگی‌های پیاده‌سازی شده

### 1. ویجت تاریخ شمسی (PersianDatePickerWidget)
- انتخابگر تاریخ شمسی با رابط کاربری فارسی
- تبدیل خودکار تاریخ شمسی به میلادی
- پشتیبانی از کتابخانه persian-datepicker

### 2. Template Tags سفارشی
- `to_persian_date`: تبدیل تاریخ میلادی به شمسی
- `persian_date_display`: نمایش زیبای تاریخ شمسی با نام ماه
- `persian_date_now`: نمایش تاریخ شمسی فعلی

### 3. فرم‌های بهبود یافته
تمام فرم‌های شامل فیلدهای تاریخ شمسی به‌روزرسانی شده‌اند:
- ProjectForm
- PeriodForm  
- TransactionForm

## نحوه استفاده

### 1. استفاده از ویجت در فرم‌ها

```python
from construction.widgets import PersianDatePickerWidget

class MyForm(forms.ModelForm):
    class Meta:
        model = MyModel
        fields = ['date_shamsi', 'date_gregorian']
        widgets = {
            'date_shamsi': PersianDatePickerWidget(),
            'date_gregorian': GregorianDatePickerWidget(),
        }
```

### 2. استفاده از Template Tags

```html
{% load persian_date_tags %}

<!-- تبدیل تاریخ میلادی به شمسی -->
{{ object.created_at|to_persian_date }}
{{ object.created_at|to_persian_date:"Y/m/d H:i" }}

<!-- نمایش زیبای تاریخ شمسی -->
{{ object.date_shamsi|persian_date_display }}

<!-- نمایش تاریخ فعلی -->
{% persian_date_now %}
{% persian_date_now "Y/m/d H:i" %}
```

### 3. ساختار فایل‌ها

```
construction/
├── static/construction/
│   ├── css/persian-calendar.css    # استایل‌های سفارشی
│   └── js/persian-calendar.js      # منطق تقویم شمسی
├── templates/construction/
│   └── persian_date_widget.html    # تمپلیت ویجت
├── templatetags/
│   └── persian_date_tags.py        # تگ‌های سفارشی
├── widgets.py                      # ویجت‌های سفارشی
└── forms.py                        # فرم‌های به‌روزرسانی شده
```

## کتابخانه‌های مورد استفاده

1. **jdatetime** (Python): تبدیل تاریخ در سمت سرور
2. **persian-date** (JavaScript): تبدیل تاریخ در مرورگر  
3. **persian-datepicker** (JavaScript): رابط کاربری تقویم

## ویژگی‌های اضافی

- تبدیل خودکار تاریخ شمسی به میلادی
- پشتیبانی از RTL و فارسی
- رابط کاربری زیبا و کاربرپسند
- سازگاری با Bootstrap 4
- پشتیبانی از موبایل

## مثال کاربرد

```python
# models.py
class Event(models.Model):
    name = models.CharField(max_length=200)
    date_shamsi = models.DateField(verbose_name="تاریخ شمسی")
    date_gregorian = models.DateField(verbose_name="تاریخ میلادی")

# forms.py  
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'date_shamsi', 'date_gregorian']
        widgets = {
            'date_shamsi': PersianDatePickerWidget(),
            'date_gregorian': GregorianDatePickerWidget(),
        }
```

```html
<!-- template -->
{% load persian_date_tags %}

<div>
    <label>تاریخ رویداد:</label>
    {{ event.date_shamsi|persian_date_display }}
</div>

<div>
    <label>ایجاد شده در:</label> 
    {{ event.created_at|to_persian_date:"Y/m/d H:i" }}
</div>
```

هر فیلد تاریخ شمسی به طور خودکار فیلد میلادی مرتبط را پر می‌کند.

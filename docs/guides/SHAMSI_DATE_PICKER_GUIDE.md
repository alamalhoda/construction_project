# راهنمای استفاده از Date Picker شمسی

این پروژه از ویجت‌های تاریخ شمسی `django-jalali` برای فرم‌های عمومی استفاده می‌کند.

## پیاده‌سازی انجام شده

### 1. فرم‌ها (forms.py)

```python
from django import forms
from django_jalali.forms import jDateField
from django_jalali.admin.widgets import AdminjDateWidget
from . import models

class ProjectForm(forms.ModelForm):
    start_date_shamsi = jDateField(
        label="تاریخ شروع (شمسی)",
        widget=AdminjDateWidget  # ویجت تاریخ شمسی
    )
    end_date_shamsi = jDateField(
        label="تاریخ پایان (شمسی)",
        widget=AdminjDateWidget
    )
    
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

### 2. تنظیمات HTML (base.html)

#### CSS Files:
```html
<!-- django-jalali Admin CSS for date widgets -->
<link rel="stylesheet" href="{% static 'admin/jquery.ui.datepicker.jalali/themes/base/jquery-ui.min.css' %}">
<link rel="stylesheet" href="{% static 'admin/css/main.css' %}">

<!-- Custom Persian Calendar CSS -->
<link rel="stylesheet" href="{% static 'construction/css/persian-calendar.css' %}">
```

#### JavaScript Files:
```html
<!-- django-jalali JavaScript files for date widgets -->
<script src="{% static 'admin/jquery.ui.datepicker.jalali/scripts/jquery-1.10.2.min.js' %}"></script>
<script src="{% static 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.core.js' %}"></script>
<script src="{% static 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc.js' %}"></script>
<script src="{% static 'admin/jquery.ui.datepicker.jalali/scripts/calendar.js' %}"></script>
<script src="{% static 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc-fa.js' %}"></script>
<script src="{% static 'admin/main.js' %}"></script>
```

#### JavaScript Initialization:
```html
<script>
    $(document).ready(function() {
        // اضافه کردن کلاس برای استایل‌دهی بهتر
        $('input[name*="shamsi"]').addClass('jalali-date-input');
        
        // تنظیم جهت متن برای فیلدهای تاریخ شمسی
        $('input[name*="shamsi"]').attr('dir', 'rtl');
    });
</script>
```

### 3. استایل‌دهی (CSS)

```css
/* استایل‌های ویجت تاریخ شمسی در فرم‌های عمومی */
.jalali-date-input {
    direction: rtl;
    background-image: url('data:image/svg+xml;utf8,<svg>...</svg>');
    background-repeat: no-repeat;
    background-position: left 10px center;
    background-size: 16px;
    padding-left: 35px;
}

/* تقویم شمسی پاپ‌آپ */
.ui-datepicker {
    direction: rtl;
    font-family: 'Tahoma', 'Vazir', sans-serif;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    background: white;
    z-index: 9999;
}

.ui-datepicker-header {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    border-radius: 8px 8px 0 0;
    padding: 10px;
    border: none;
}
```

## ویژگی‌های Date Picker شمسی

### 1. ویژگی‌های کاربری
- **تقویم شمسی کامل**: نمایش ماه‌ها و روزهای هفته به فارسی
- **ناوبری آسان**: دکمه‌های قبل/بعد برای تغییر ماه و سال
- **انتخاب سریع**: کلیک روی تاریخ برای انتخاب
- **تاریخ امروز**: مشخص کردن تاریخ فعلی
- **جهت راست به چپ**: سازگار با زبان فارسی

### 2. ویژگی‌های فنی
- **یکپارچگی با Django**: کار با فرم‌ها و validation
- **سازگاری با Bootstrap**: طراحی responsive
- **CSS قابل تنظیم**: امکان شخصی‌سازی ظاهر
- **JavaScript مستقل**: عدم وابستگی به کتابخانه‌های خارجی

## نحوه استفاده در پروژه‌های جدید

### 1. اضافه کردن فیلد تاریخ شمسی به فرم

```python
from django_jalali.forms import jDateField
from django_jalali.admin.widgets import AdminjDateWidget

class MyForm(forms.ModelForm):
    my_date = jDateField(
        label="تاریخ مورد نظر",
        widget=AdminjDateWidget,
        required=True
    )
    
    class Meta:
        model = MyModel
        fields = ['my_date']
```

### 2. اضافه کردن به Template

```html
<div class="form-group row">
    <label class="col-sm-3 col-form-label" for="{{ form.my_date.id_for_label }}">
        {{ form.my_date.label }}:
    </label>
    <div class="col-sm-9">
        {{ form.my_date }}
    </div>
</div>
```

### 3. تنظیمات اضافی

```python
# در صورت نیاز به تنظیمات خاص
my_date = jDateField(
    label="تاریخ مورد نظر",
    widget=AdminjDateWidget(attrs={
        'class': 'form-control custom-class',
        'placeholder': 'انتخاب تاریخ...'
    }),
    help_text="تاریخ را به فرمت شمسی وارد کنید"
)
```

## نکات مهم

### 1. فایل‌های استاتیک
- حتماً `python manage.py collectstatic` را اجرا کنید
- `STATIC_ROOT` در settings.py تنظیم شده باشد

### 2. ترتیب لود JavaScript
- jQuery باید قبل از فایل‌های django-jalali لود شود
- فایل‌های jalali باید به ترتیب صحیح لود شوند

### 3. CSS Conflicts
- ممکن است با استایل‌های Bootstrap تداخل داشته باشد
- CSS سفارشی را بعد از fایل‌های django-jalali لود کنید

### 4. زمان‌بندی
- ویجت‌ها بعد از لود کامل DOM فعال می‌شوند
- برای فرم‌های AJAX باید دوباره initialize کنید

## عیب‌یابی مشکلات رایج

### 1. Date Picker ظاهر نمی‌شود
- بررسی کنید که jQuery لود شده باشد
- فایل‌های CSS و JS django-jalali موجود باشند
- Console browser را برای خطاهای JavaScript بررسی کنید

### 2. استایل‌ها صحیح نیستند
- `collectstatic` را اجرا کنید
- مسیر فایل‌های استاتیک را بررسی کنید
- Cache browser را پاک کنید

### 3. تاریخ ذخیره نمی‌شود
- بررسی کنید مدل از `jDateField` استفاده کند
- validation errors را چک کنید
- فرمت تاریخ ورودی را بررسی کنید

## مثال کامل

```html
<!-- Template -->
{% load static %}
{% load jformat %}

<form method="post">
    {% csrf_token %}
    
    <div class="form-group row">
        <label class="col-sm-3 col-form-label">
            {{ form.start_date_shamsi.label }}:
        </label>
        <div class="col-sm-9">
            {{ form.start_date_shamsi }}
            {% if form.start_date_shamsi.errors %}
                <div class="text-danger">
                    {{ form.start_date_shamsi.errors }}
                </div>
            {% endif %}
        </div>
    </div>
    
    <button type="submit" class="btn btn-primary">ذخیره</button>
</form>
```

اکنون در فرم‌های شما انتخابگر تاریخ شمسی کاملاً فعال است! 🎉

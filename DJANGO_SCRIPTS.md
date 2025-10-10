# اسکریپت‌های Django

این پروژه شامل اسکریپت‌هایی برای اجرای آسان دستورات Django است.

## اسکریپت‌های موجود

### 1. `run_django.sh` (Bash)
اسکریپت Bash برای اجرای دستورات Django با فعال‌سازی خودکار محیط مجازی.

```bash
# استفاده
./run_django.sh [دستورات Django]

# مثال‌ها
./run_django.sh migrate construction
./run_django.sh runserver
./run_django.sh shell
./run_django.sh makemigrations
```

### 2. `run_django.py` (Python)
اسکریپت Python برای اجرای دستورات Django با فعال‌سازی خودکار محیط مجازی.

```bash
# استفاده
python3 run_django.py [دستورات Django]

# مثال‌ها
python3 run_django.py migrate construction
python3 run_django.py runserver
python3 run_django.py shell
python3 run_django.py makemigrations
```

## ویژگی‌ها

- ✅ **فعال‌سازی خودکار محیط مجازی**: نیازی به `source env/bin/activate` نیست
- ✅ **بررسی وجود محیط مجازی**: اگر `env` وجود نداشته باشد، خطا می‌دهد
- ✅ **پیام‌های واضح**: وضعیت محیط مجازی و اجرای دستورات را نشان می‌دهد
- ✅ **پشتیبانی از همه دستورات Django**: `migrate`, `runserver`, `shell`, `makemigrations` و...

## استفاده پیشنهادی

برای راحتی بیشتر، می‌توانید alias ایجاد کنید:

```bash
# در ~/.bashrc یا ~/.zshrc
alias dj='./run_django.sh'
alias djp='python3 run_django.py'

# سپس استفاده کنید
dj migrate construction
djp runserver
```

## دستورات سفارشی (Custom Management Commands)

### 3. `export_excel` - تولید فایل Excel
دستور سفارشی برای تولید فایل Excel شامل تمام اطلاعات و محاسبات پروژه.

```bash
# استفاده پایه
python manage.py export_excel

# یا با اسکریپت‌های کمکی
./run_django.sh export_excel
python3 run_django.py export_excel
```

#### گزینه‌های موجود:

**`--output` یا `-o`**: مسیر و نام فایل خروجی
```bash
python manage.py export_excel --output my_report.xlsx
python manage.py export_excel -o /path/to/reports/project_report.xlsx
```

**`--project-id` یا `-p`**: شناسه پروژه خاص
```bash
python manage.py export_excel --project-id 2
python manage.py export_excel -p 1
```

**`--open`**: باز کردن خودکار فایل بعد از تولید
```bash
python manage.py export_excel --open
```

**`--force` یا `-f`**: بازنویسی فایل در صورت وجود
```bash
python manage.py export_excel --output report.xlsx --force
```

#### مثال‌های کاربردی:

```bash
# تولید فایل با نام پیش‌فرض
python manage.py export_excel

# تولید فایل با نام دلخواه
python manage.py export_excel --output monthly_report.xlsx

# تولید فایل برای پروژه خاص
python manage.py export_excel --project-id 2 --output project2.xlsx

# تولید و باز کردن خودکار
python manage.py export_excel --open

# بازنویسی فایل موجود
python manage.py export_excel --output report.xlsx --force
```

#### محتویات فایل Excel:

**شیت‌های داده پایه (9 شیت):**
- Project: اطلاعات پروژه
- Units: واحدهای پروژه
- Investors: سرمایه‌گذاران (همه 34 نفر)
- Periods: دوره‌های زمانی
- InterestRates: نرخ‌های سود
- Transactions: تراکنش‌ها
- Expenses: هزینه‌ها
- Sales: فروش/مرجوعی
- UserProfiles: پروفایل کاربران

**شیت‌های محاسباتی (6 شیت):**
- Dashboard: خلاصه کلی پروژه
- Profit_Metrics: محاسبات سود
- Cost_Metrics: محاسبات هزینه
- Investor_Analysis: تحلیل سرمایه‌گذاران (همه 34 نفر)
- Period_Summary: خلاصه دوره‌ای
- Transaction_Summary: خلاصه تراکنش‌ها

#### نکات مهم:

- ✅ **همه سرمایه‌گذاران**: هر دو شیت Investors و Investor_Analysis شامل همه 34 سرمایه‌گذار هستند
- ✅ **محاسبات سرور**: تمام محاسبات در سرور انجام می‌شود (Static)
- ✅ **پشتیبانی فارسی**: فونت Tahoma و پشتیبانی کامل از زبان فارسی
- ✅ **فرمت اعداد**: اعداد با جداکننده هزارگان نمایش داده می‌شوند
- ✅ **تاریخ شمسی و میلادی**: هر دو نوع تاریخ در فایل موجود است

## نکات مهم

1. همیشه از پوشه اصلی پروژه Django اجرا کنید
2. مطمئن شوید که فایل `manage.py` در همان پوشه وجود دارد
3. محیط مجازی باید در پوشه `env` باشد
4. برای دستور `export_excel` نیاز به کتابخانه `openpyxl` دارید (از قبل نصب شده)

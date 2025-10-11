# 📋 Django Management Commands

این پوشه شامل دستورات سفارشی Django برای مدیریت پروژه است.

## 📊 دستور `export_excel`

تولید فایل Excel جامع شامل تمام اطلاعات و محاسبات مالی پروژه به دو صورت **Static** و **Dynamic**.

### 🚀 استفاده سریع

```bash
# تولید فایل Static (پیش‌فرض)
python manage.py export_excel

# تولید فایل Dynamic با فرمول‌های محاسباتی
python manage.py export_excel --dynamic

# تولید Dynamic با نام دلخواه و باز کردن خودکار
python manage.py export_excel --dynamic --output my_report.xlsx --open
```

### 📖 گزینه‌های کامل

| گزینه | مخفف | توضیح | مثال |
|--------|------|-------|------|
| `--output` | `-o` | مسیر و نام فایل خروجی | `--output report.xlsx` |
| `--project-id` | `-p` | شناسه پروژه خاص | `--project-id 2` |
| `--dynamic` | `-d` | تولید فایل Dynamic با فرمول | `--dynamic` |
| `--open` | - | باز کردن خودکار فایل | `--open` |
| `--force` | `-f` | بازنویسی فایل موجود | `--force` |
| `--help` | `-h` | نمایش راهنما | `--help` |

### 🔄 تفاوت Static و Dynamic

#### 📌 فایل Static (پیش‌فرض)

**مناسب برای**: آرشیو، ارسال به دیگران، گزارش‌گیری ثابت

**ویژگی‌ها**:
- ✅ **مقادیر ثابت**: تمام محاسبات در سرور انجام می‌شود و نتایج نهایی ذخیره می‌شود
- ✅ **سرعت بالا**: باز شدن فایل بسیار سریع است
- ✅ **سازگاری کامل**: روی تمام نسخه‌های Excel کار می‌کند
- ✅ **حجم کمتر**: فایل کوچک‌تر و سبک‌تر
- ✅ **عدم نیاز به تخصص**: هر کسی می‌تواند استفاده کند
- ⚠️ **غیرقابل تغییر**: با تغییر داده‌ها، محاسبات به‌روز نمی‌شود

**شیت‌ها** (15 شیت):
- 9 شیت داده پایه + 6 شیت محاسباتی با مقادیر ثابت

#### ⚡ فایل Dynamic (پیشرفته)

**مناسب برای**: تحلیل تعاملی، بررسی سناریوها، کار تیمی

**ویژگی‌ها**:
- 🔥 **فرمول‌های زنده**: تمام محاسبات با فرمول Excel انجام می‌شود
- 🔥 **به‌روزرسانی خودکار**: با تغییر داده‌ها، تمام محاسبات آپدیت می‌شود
- 🔥 **Named Ranges**: دسترسی آسان به داده‌ها با نام
- 🔥 **قابل تغییر**: می‌توانید داده‌ها را تغییر دهید و نتایج را ببینید
- 🔥 **شفافیت کامل**: تمام فرمول‌ها قابل مشاهده و بررسی هستند
- 🔥 **شیت راهنما**: شامل فهرست و راهنمای فرمول‌ها
- ⚠️ **نیاز به Excel قوی**: ممکن است روی نسخه‌های قدیمی کند باشد
- ⚠️ **حجم بیشتر**: فایل بزرگ‌تر است

**شیت‌ها** (17 شیت):
- 📋 فهرست (Table of Contents)
- 📖 راهنمای فرمول‌ها (Formula Guide)
- 9 شیت داده پایه
- 6 شیت محاسباتی با فرمول‌های زنده

### 📊 مقایسه جامع

| ویژگی | Static | Dynamic |
|-------|--------|---------|
| **محاسبات** | در سرور | در Excel با فرمول |
| **سرعت باز شدن** | ⚡ خیلی سریع | 🐌 کندتر (بسته به حجم) |
| **قابلیت تغییر** | ❌ ثابت | ✅ تعاملی |
| **شفافیت** | 📊 نتایج نهایی | 🔍 فرمول‌ها قابل مشاهده |
| **سازگاری** | ✅ همه نسخه‌ها | ⚠️ Excel 2016+ |
| **حجم فایل** | 📁 کوچک | 📦 بزرگ‌تر |
| **مناسب برای** | 📄 آرشیو، گزارش | 🔬 تحلیل، بررسی |
| **Named Ranges** | ❌ ندارد | ✅ دارد |
| **راهنما** | ❌ ندارد | ✅ دارد |
| **تعداد شیت** | 15 شیت | 17 شیت |

### 📁 ساختار فایل Excel

#### 📄 ساختار Static (15 شیت)

**شیت‌های داده پایه** (9 شیت):
1. **Project** - اطلاعات کامل پروژه فعال
2. **Units** - لیست کامل واحدها با متراژ و قیمت
3. **Investors** - همه سرمایه‌گذاران
4. **Periods** - دوره‌های زمانی پروژه
5. **InterestRates** - نرخ‌های سود
6. **Transactions** - تمام تراکنش‌ها
7. **Expenses** - هزینه‌های پروژه
8. **Sales** - فروش و مرجوعی‌ها
9. **UserProfiles** - پروفایل کاربران

**شیت‌های محاسباتی** (6 شیت):
1. **Dashboard** - خلاصه کلی پروژه (مقادیر ثابت)
2. **Profit_Metrics** - محاسبات سود (مقادیر محاسبه شده)
3. **Cost_Metrics** - محاسبات هزینه و ارزش (مقادیر محاسبه شده)
4. **Investor_Analysis** - تحلیل تفصیلی سرمایه‌گذاران (مقادیر ثابت)
5. **Period_Summary** - خلاصه دوره‌ای با مقادیر تجمعی (مقادیر ثابت)
6. **Transaction_Summary** - خلاصه تراکنش‌ها (مقادیر ثابت)

#### ⚡ ساختار Dynamic (17 شیت)

**شیت‌های راهنما** (2 شیت):
1. **📋 فهرست** - Table of Contents با لینک به تمام شیت‌ها
2. **📖 راهنمای فرمول‌ها** - توضیح Named Ranges و فرمول‌ها

**شیت‌های داده پایه** (9 شیت) - مشابه Static

**شیت‌های محاسباتی با فرمول** (6 شیت):
1. **Comprehensive_Metrics** - داشبورد جامع با فرمول‌های Excel
2. **Transaction_Profit_Calculations** - محاسبات سود با فرمول
3. **PeriodExpenseSummary** - خلاصه هزینه‌ها با فرمول
4. **Investor_Analysis_Dynamic** - تحلیل سرمایه‌گذاران با فرمول
5. **Period_Summary_Dynamic** - خلاصه دوره‌ای با فرمول
6. **Transaction_Summary_Dynamic** - خلاصه تراکنش‌ها با فرمول

**ویژگی منحصر به فرد Dynamic**:
- 🔗 **Named Ranges**: دسترسی سریع به داده‌ها (مثل `TotalInvestors`, `ProjectExpenses`)
- 🧮 **فرمول‌های پیشرفته**: SUMIFS, VLOOKUP, INDEX-MATCH
- 🔄 **محاسبات خودکار**: تغییر هر سلول، کل فایل را آپدیت می‌کند
- 📊 **قابلیت تحلیل**: می‌توانید سناریوهای مختلف را تست کنید

### 💡 مثال‌های کاربردی

#### 1. گزارش Static ماهانه (برای آرشیو)
```bash
python manage.py export_excel \
  --output "reports/monthly_static_$(date +%Y%m).xlsx"
```

#### 2. گزارش Dynamic برای تحلیل
```bash
python manage.py export_excel \
  --dynamic \
  --output "analysis/project_dynamic_$(date +%Y%m%d).xlsx" \
  --open
```

#### 3. گزارش پروژه خاص (Static)
```bash
python manage.py export_excel \
  --project-id 2 \
  --output "project_2_static.xlsx"
```

#### 4. گزارش پروژه خاص (Dynamic)
```bash
python manage.py export_excel \
  --dynamic \
  --project-id 2 \
  --output "project_2_dynamic.xlsx"
```

#### 5. گزارش سریع Static و باز کردن
```bash
python manage.py export_excel --open
```

#### 6. گزارش سریع Dynamic و باز کردن
```bash
python manage.py export_excel --dynamic --open
```

#### 7. بازنویسی گزارش روزانه
```bash
python manage.py export_excel \
  --output daily_report.xlsx \
  --force
```

#### 8. مقایسه Static و Dynamic
```bash
# ابتدا Static تولید کنید
python manage.py export_excel --output compare_static.xlsx

# سپس Dynamic تولید کنید
python manage.py export_excel --dynamic --output compare_dynamic.xlsx

# حالا می‌توانید دو فایل را مقایسه کنید
```

### ✨ ویژگی‌های مشترک

- ✅ **همه سرمایه‌گذاران**: شامل همه سرمایه‌گذاران (نه فقط آن‌هایی که واحد دارند)
- ✅ **محاسبات دقیق**: Static در سرور، Dynamic با فرمول Excel
- ✅ **پشتیبانی فارسی**: فونت Tahoma و راست‌چین
- ✅ **فرمت‌بندی اعداد**: جداکننده هزارگان (۱۲۳,۴۵۶,۷۸۹)
- ✅ **تاریخ دوگانه**: شمسی (۱۴۰۳/۰۷/۱۹) و میلادی
- ✅ **استایل حرفه‌ای**: رنگ‌بندی، Border، و فرمت‌های مناسب
- ✅ **داده‌های کامل**: تمام اطلاعات پروژه در یک فایل

### 🎯 چه زمانی از کدام استفاده کنیم؟

#### استفاده از Static 📄
- ✅ آرشیو گزارش‌های ماهانه/سالانه
- ✅ ارسال به مشتریان یا سرمایه‌گذاران
- ✅ چاپ گزارش‌ها
- ✅ زمانی که سرعت مهم است
- ✅ استفاده در سیستم‌های ضعیف
- ✅ اطمینان از ثبات داده‌ها

#### استفاده از Dynamic ⚡
- ✅ تحلیل تعاملی داده‌ها
- ✅ بررسی سناریوهای مختلف (What-if Analysis)
- ✅ کار تیمی روی یک فایل
- ✅ آموزش و یادگیری
- ✅ مشاهده فرمول‌های محاسباتی
- ✅ بررسی دقیق محاسبات
- ✅ توسعه و تست محاسبات جدید

### 🔧 نیازمندی‌ها

```python
openpyxl>=3.1.0  # از قبل نصب شده
```

**برای Dynamic**:
- Microsoft Excel 2016 یا جدیدتر (توصیه می‌شود)
- حداقل 4GB RAM برای فایل‌های بزرگ
- پردازنده قوی برای محاسبات پیچیده

### 📝 نکات مهم

#### نکات عمومی
1. **پروژه فعال**: اگر `--project-id` مشخص نشود، از پروژه فعال استفاده می‌شود
2. **نام فایل پیش‌فرض Static**: `project_<نام>_static_<تاریخ>.xlsx`
3. **نام فایل پیش‌فرض Dynamic**: `project_<نام>_dynamic_<تاریخ>.xlsx`
4. **محل ذخیره**: پوشه فعلی (یا مسیر مشخص شده در `--output`)
5. **بازنویسی**: بدون `--force` روی فایل موجود خطا می‌دهد

#### نکات ویژه Static
- ⚡ باز شدن فوری، حتی برای پروژه‌های بزرگ
- 💾 حجم فایل کمتر (حدود 50-200 KB)
- 🔒 داده‌ها ثابت و غیرقابل تغییر
- ✅ مناسب برای اسناد رسمی

#### نکات ویژه Dynamic
- 🐌 زمان باز شدن بیشتر (10-30 ثانیه بسته به حجم)
- 💾 حجم فایل بیشتر (حدود 200-500 KB)
- 🔓 داده‌ها قابل تغییر و تحلیل
- 🔍 فرمول‌ها قابل مشاهده و ویرایش
- ⚠️ Enable Editing کنید تا محاسبات به‌روز شوند
- 📊 مناسب برای تحلیل و گزارش‌گیری داخلی

### 🐛 عیب‌یابی

#### خطا: "هیچ پروژه فعالی یافت نشد"
```bash
# راه‌حل: مشخص کردن ID پروژه
python manage.py export_excel --project-id 1
```

#### خطا: "فایل از قبل وجود دارد"
```bash
# راه‌حل: استفاده از --force
python manage.py export_excel --output report.xlsx --force
```

#### خطا: "Permission denied"
```bash
# راه‌حل: بررسی دسترسی پوشه یا تغییر مسیر
python manage.py export_excel --output ~/Desktop/report.xlsx
```

#### مشکل: فایل Dynamic کند باز می‌شود
```
راه‌حل‌ها:
1. صبر کنید تا Excel تمام فرمول‌ها را محاسبه کند (10-30 ثانیه)
2. از Excel 2016 یا جدیدتر استفاده کنید
3. RAM سیستم را افزایش دهید
4. برای گزارش‌های سریع از Static استفاده کنید
```

#### مشکل: محاسبات Dynamic به‌روز نمی‌شود
```
راه‌حل‌ها:
1. در Excel روی "Enable Editing" کلیک کنید
2. Ctrl+Alt+F9 برای Recalculate All
3. File > Options > Formulas > Calculation Options = Automatic
```

#### مشکل: فرمول‌ها به جای نتیجه نمایش داده می‌شود
```
راه‌حل:
1. Ctrl+` برای تغییر حالت نمایش
2. یا از منوی Excel: Formulas > Show Formulas
```

#### مشکل: خطای "#REF!" در فرمول‌های Dynamic
```
راه‌حل:
1. فایل را ببندید و دوباره باز کنید
2. فایل جدید تولید کنید
3. از نسخه به‌روز Excel استفاده کنید
```

### 📊 مقایسه سریع: کدام را انتخاب کنم؟

| سناریو | توصیه |
|--------|-------|
| گزارش ماهانه برای مدیریت | Static ⚡ |
| آرشیو پایان سال | Static ⚡ |
| ارسال به حسابدار | Static ⚡ |
| چاپ گزارش | Static ⚡ |
| تحلیل عمیق داده‌ها | Dynamic 🔥 |
| بررسی سناریوهای مختلف | Dynamic 🔥 |
| آموزش به همکاران | Dynamic 🔥 |
| بررسی فرمول‌های محاسباتی | Dynamic 🔥 |
| ارسال به سرمایه‌گذاران | Static ⚡ |
| کار تیمی روی یک فایل | Dynamic 🔥 |
| نیاز به سرعت بالا | Static ⚡ |
| نیاز به شفافیت کامل | Dynamic 🔥 |

### 💡 نکته طلایی

**برای بهترین نتیجه**: 
- هر ماه یک فایل **Static** برای آرشیو تولید کنید 📄
- یک فایل **Dynamic** برای تحلیل روزمره نگه دارید ⚡
- قبل از ارائه به مشتری، **Static** استفاده کنید 🎯

### 📞 پشتیبانی

برای گزارش مشکلات یا پیشنهادات، به مستندات اصلی پروژه مراجعه کنید:
- 📖 [STATIC_EXCEL_DOCUMENTATION.md](../../docs/STATIC_EXCEL_DOCUMENTATION.md)
- ⚡ [DYNAMIC_EXCEL_DOCUMENTATION.md](../../docs/DYNAMIC_EXCEL_DOCUMENTATION.md)
- 🚀 [DYNAMIC_EXCEL_QUICK_REFERENCE.md](../../docs/DYNAMIC_EXCEL_QUICK_REFERENCE.md)

---

**تاریخ ایجاد**: 2025-10-10  
**نسخه**: 1.0  
**وضعیت**: فعال و آماده استفاده

## 🔄 دستور `convert_rial_to_toman`

تبدیل تمام فیلدهای رقمی پروژه از ریال به تومان (تقسیم بر ۱۰).

### 🚀 استفاده سریع

```bash
# نمایش تغییرات بدون اعمال
python manage.py convert_rial_to_toman --dry-run

# تبدیل با بکاپ خودکار
python manage.py convert_rial_to_toman --backup

# تبدیل مستقیم (احتیاط!)
python manage.py convert_rial_to_toman
```

### 📖 گزینه‌های کامل

| گزینه | توضیح | مثال |
|--------|-------|------|
| `--dry-run` | نمایش تغییرات بدون اعمال | `--dry-run` |
| `--backup` | ایجاد بکاپ قبل از تبدیل | `--backup` |
| `--help` | نمایش راهنما | `--help` |

### 🔄 موارد تبدیل شده

1. **Units** - قیمت هر متر و قیمت کل
2. **Transactions** - مبلغ تراکنش‌ها
3. **Expenses** - مبلغ هزینه‌ها
4. **Sales** - مبلغ فروش و مرجوعی
5. **InterestRates** - بررسی می‌شود (نیازی به تبدیل ندارد)

### ⚠️ نکات مهم

- **همیشه بکاپ بگیرید**: قبل از اجرا حتماً `--backup` استفاده کنید
- **ابتدا تست کنید**: با `--dry-run` تغییرات را ببینید
- **برگشت‌ناپذیر**: بدون بکاپ امکان بازگشت وجود ندارد
- **Transaction Safe**: در صورت خطا، تمام تغییرات rollback می‌شود

### 💡 مثال‌های کاربردی

```bash
# مرحله 1: بررسی تغییرات
python manage.py convert_rial_to_toman --dry-run

# مرحله 2: تبدیل با بکاپ
python manage.py convert_rial_to_toman --backup
```

---

## 🕐 دستور `check_timezone`

بررسی تنظیمات timezone و نمایش زمان فعلی در فرمت‌های مختلف.

### 🚀 استفاده سریع

```bash
# بررسی timezone
python manage.py check_timezone
```

### 📊 اطلاعات نمایش داده شده

1. **تنظیمات Django**: TIME_ZONE, USE_TZ, USE_I18N, USE_L10N
2. **زمان‌های فعلی**: UTC, تهران, Django
3. **متغیر محیطی**: TZ
4. **زمان فارسی**: فرمت شمسی

### ✨ ویژگی‌ها

- ✅ نمایش تنظیمات timezone پروژه
- ✅ مقایسه زمان UTC و تهران
- ✅ بررسی متغیرهای محیطی
- ✅ تست فرمت فارسی

---

## 📥 دستور `download_online_db`

دانلود دیتابیس آنلاین از GitHub و جایگزینی با دیتابیس محلی.

### 🚀 استفاده سریع

```bash
# دانلود با تأیید
python manage.py download_online_db --confirm

# دانلود با بکاپ محلی
python manage.py download_online_db --confirm --backup-local

# دانلود از شاخه خاص
python manage.py download_online_db --confirm --branch chabokan-deployment
```

### 📖 گزینه‌های کامل

| گزینه | توضیح | مثال |
|--------|-------|------|
| `--confirm` | تأیید جایگزینی (الزامی) | `--confirm` |
| `--backup-local` | بکاپ دیتابیس محلی | `--backup-local` |
| `--branch` | شاخه Git (پیش‌فرض: master) | `--branch master` |

### ⚠️ نکات مهم

- **تأیید الزامی**: بدون `--confirm` اجرا نمی‌شود
- **بررسی Git**: تغییرات uncommitted نباید وجود داشته باشد
- **Stash خودکار**: تغییرات محلی موقتاً stash می‌شود
- **Restore خودکار**: پس از pull، تغییرات restore می‌شود

### 💡 مثال‌های کاربردی

```bash
# دانلود امن با بکاپ
python manage.py download_online_db --confirm --backup-local

# دانلود از شاخه خاص
python manage.py download_online_db --confirm --branch chabokan-deployment
```

---

## 📤 دستور `upload_local_db`

آپلود دیتابیس محلی به GitHub و جایگزینی دیتابیس آنلاین.

### 🚀 استفاده سریع

```bash
# آپلود با تأیید
python manage.py upload_local_db --confirm

# آپلود با بکاپ آنلاین
python manage.py upload_local_db --confirm --backup-online

# آپلود با پیام commit سفارشی
python manage.py upload_local_db --confirm --commit-message "Updated investor data"
```

### 📖 گزینه‌های کامل

| گزینه | توضیح | مثال |
|--------|-------|------|
| `--confirm` | تأیید جایگزینی (الزامی) | `--confirm` |
| `--backup-online` | بکاپ دیتابیس آنلاین | `--backup-online` |
| `--commit-message` | پیام commit | `--commit-message "message"` |

### 🔄 فرآیند آپلود

1. بررسی وجود دیتابیس محلی
2. ایجاد بکاپ از دیتابیس آنلاین (اختیاری)
3. کپی دیتابیس محلی به آنلاین
4. اضافه کردن به Git
5. Commit تغییرات
6. Push به GitHub

### ⚠️ نکات مهم

- **تأیید الزامی**: بدون `--confirm` اجرا نمی‌شود
- **بکاپ توصیه می‌شود**: همیشه `--backup-online` استفاده کنید
- **Push به master**: تغییرات به شاخه master push می‌شود
- **برگشت‌ناپذیر**: بدون بکاپ امکان بازگشت وجود ندارد

### 💡 مثال‌های کاربردی

```bash
# آپلود امن با بکاپ
python manage.py upload_local_db --confirm --backup-online

# آپلود با پیام توضیحی
python manage.py upload_local_db \
  --confirm \
  --backup-online \
  --commit-message "Added new investors and updated transactions"
```

---

## 🔒 دستور `security_check`

بررسی جامع امنیتی پروژه و شناسایی مشکلات امنیتی.

### 🚀 استفاده سریع

```bash
# بررسی کامل امنیتی
python manage.py security_check

# بررسی نوع خاص
python manage.py security_check --check-type settings

# بررسی و رفع مشکلات
python manage.py security_check --fix-issues
```

### 📖 گزینه‌های کامل

| گزینه | توضیح | مثال |
|--------|-------|------|
| `--check-type` | نوع بررسی | `--check-type all` |
| `--fix-issues` | رفع خودکار مشکلات | `--fix-issues` |

### 🔍 انواع بررسی

| نوع | توضیح |
|-----|-------|
| `all` | بررسی کامل (پیش‌فرض) |
| `settings` | تنظیمات امنیتی Django |
| `data` | یکپارچگی داده‌ها |
| `monitoring` | نظارت امنیتی |
| `cleanup` | پاک‌سازی داده‌های قدیمی |

### 🔧 موارد بررسی شده

#### 1. Settings
- وضعیت DEBUG
- تنظیمات ALLOWED_HOSTS
- طول SECRET_KEY
- سایر تنظیمات امنیتی

#### 2. Data Integrity
- یکپارچگی داده‌ها
- روابط مدل‌ها
- داده‌های ناقص یا نامعتبر

#### 3. Security Monitoring
- رویدادهای امنیتی 24 ساعت گذشته
- تلاش‌های ورود ناموفق
- IP های مشکوک
- فعالیت‌های غیرعادی

#### 4. Cleanup
- Session های قدیمی
- لاگ‌های منقضی شده
- آرشیو داده‌های قدیمی

### 💡 مثال‌های کاربردی

```bash
# بررسی کامل
python manage.py security_check

# فقط بررسی تنظیمات
python manage.py security_check --check-type settings

# بررسی و رفع مشکلات داده
python manage.py security_check --check-type data --fix-issues

# پاک‌سازی داده‌های قدیمی
python manage.py security_check --check-type cleanup
```

### 📊 خروجی نمونه

```
🔒 شروع بررسی امنیتی پروژه

🔧 بررسی تنظیمات امنیتی:
✅ DEBUG = False
✅ ALLOWED_HOSTS تنظیم شده
✅ SECRET_KEY طول مناسب دارد

📊 بررسی یکپارچگی داده‌ها:
✅ هیچ مشکل یکپارچگی یافت نشد

👁️ بررسی نظارت امنیتی:
📈 رویدادهای 24 ساعت گذشته: 156
🚨 رویدادهای بحرانی: 0
🔐 تلاش‌های ورود ناموفق: 2
⚠️ IP های مشکوک: 0

🧹 پاک کردن داده‌های قدیمی:
🗑️ 45 session قدیمی حذف شد
🗑️ 128 لاگ قدیمی حذف شد

✅ بررسی امنیتی تکمیل شد
```

---

## 📚 خلاصه دستورات

| دستور | توضیح مختصر | استفاده رایج |
|-------|-------------|--------------|
| `export_excel` | تولید گزارش Excel (Static/Dynamic) | Static: `--open`<br>Dynamic: `--dynamic --open` |
| `convert_rial_to_toman` | تبدیل واحد پولی | `--backup --dry-run` |
| `check_timezone` | بررسی timezone | فقط اجرا کنید |
| `download_online_db` | دانلود دیتابیس از GitHub | `--confirm --backup-local` |
| `upload_local_db` | آپلود دیتابیس به GitHub | `--confirm --backup-online` |
| `security_check` | بررسی امنیتی جامع | `--check-type all` |

### 🎯 دستورات پرکاربرد

```bash
# گزارش Static سریع
python manage.py export_excel --open

# گزارش Dynamic تحلیلی
python manage.py export_excel --dynamic --open

# تبدیل ریال به تومان (با احتیاط!)
python manage.py convert_rial_to_toman --dry-run
python manage.py convert_rial_to_toman --backup

# همگام‌سازی دیتابیس
python manage.py download_online_db --confirm --backup-local  # دانلود
python manage.py upload_local_db --confirm --backup-online    # آپلود

# بررسی امنیتی
python manage.py security_check
```

## 🛠️ نکات عمومی

### محیط مجازی

همیشه قبل از اجرای دستورات، محیط مجازی را فعال کنید:

```bash
source env/bin/activate
```

یا از اسکریپت‌های کمکی استفاده کنید:

```bash
./run_django.sh [دستور]
python3 run_django.py [دستور]
```

### لاگ‌گیری

تمام دستورات خروجی مفیدی تولید می‌کنند. برای ذخیره لاگ:

```bash
python manage.py [دستور] > logs/command_$(date +%Y%m%d_%H%M%S).log 2>&1
```

### بکاپ

قبل از اجرای دستورات تغییردهنده (مثل `convert_rial_to_toman` یا `upload_local_db`)، **حتماً** بکاپ بگیرید:

```bash
python manage.py convert_rial_to_toman --backup
python manage.py upload_local_db --confirm --backup-online
```

### عیب‌یابی

اگر دستوری خطا داد:

1. محیط مجازی را بررسی کنید
2. لاگ خطا را بخوانید
3. از `--help` برای راهنمای دستور استفاده کنید
4. در صورت لزوم از `--dry-run` استفاده کنید

---

**آخرین به‌روزرسانی**: 2025-10-10  
**نسخه**: 2.1 - افزودن مستندات کامل Static/Dynamic Excel  
**وضعیت**: فعال، کامل و به‌روز


# 📚 مرجع API های محاسبات مالی

## 🎯 هدف
این فایل شامل تمام API های موجود برای محاسبات مالی است که در سمت سرور پیاده‌سازی شده‌اند.

---

## 📋 فهرست API های موجود

### 🏗️ **Project APIs**

#### 1. تحلیل جامع پروژه
- **Endpoint**: `GET /api/v1/Project/comprehensive_analysis/`
- **توضیح**: دریافت تمام آمار و محاسبات پروژه در یک درخواست
- **پاسخ شامل**:
  - اطلاعات پروژه
  - آمار واحدها
  - آمار تراکنش‌ها
  - آمار هزینه‌ها
  - آمار سرمایه‌گذاران
  - متریک‌های سود
  - نرخ سود فعلی

#### 2. متریک‌های سود
- **Endpoint**: `GET /api/v1/Project/profit_metrics/`
- **توضیح**: محاسبه درصدهای سود (کل، سالانه، ماهانه، روزانه)
- **پاسخ شامل**:
  - `total_profit_percentage`: درصد سود کل
  - `annual_profit_percentage`: درصد سود سالانه
  - `monthly_profit_percentage`: درصد سود ماهانه
  - `daily_profit_percentage`: درصد سود روزانه
  - `average_construction_period`: دوره متوسط ساخت
  - `correction_factor`: ضریب اصلاحی

#### 3. متریک‌های هزینه
- **Endpoint**: `GET /api/v1/Project/cost_metrics/`
- **توضیح**: محاسبه متریک‌های هزینه و ارزش
- **پاسخ شامل**:
  - `final_cost`: هزینه نهایی
  - `final_profit_amount`: سود نهایی
  - `total_profit_percentage`: درصد سود کل
  - `net_cost_per_meter`: هزینه هر متر خالص
  - `gross_cost_per_meter`: هزینه هر متر ناخالص
  - `value_per_meter`: ارزش هر متر
  - `total_expenses`: مجموع هزینه‌ها
  - `total_sales`: مجموع فروش‌ها
  - `total_value`: ارزش کل
  - `total_area`: متراژ کل
  - `total_infrastructure`: زیربنای کل

#### 4. آمار تفصیلی پروژه
- **Endpoint**: `GET /api/v1/Project/project_statistics_detailed/`
- **توضیح**: آمار کامل پروژه
- **پاسخ شامل**:
  - اطلاعات پروژه
  - آمار واحدها
  - آمار تراکنش‌ها
  - آمار هزینه‌ها
  - آمار سرمایه‌گذاران
  - زمان‌بندی پروژه

#### 5. Export فایل Excel Static (فاز اول)
- **Endpoint**: `GET /api/v1/Project/export_excel_static/`
- **توضیح**: دریافت فایل Excel با محاسبات انجام شده در سرور
- **نوع**: Static (محاسبات در سرور انجام می‌شود)
- **فرمت خروجی**: فایل Excel (.xlsx)
- **نام فایل**: `project_{نام_پروژه}_{تاریخ_و_زمان}.xlsx`

#### 6. Export فایل Excel Dynamic (فاز دوم - جدید)
- **Endpoint**: `GET /api/v1/Project/export_excel_dynamic/`
- **توضیح**: دریافت فایل Excel با فرمول‌های محاسباتی
- **نوع**: Dynamic (فرمول‌های Excel برای محاسبات)
- **فرمت خروجی**: فایل Excel (.xlsx)
- **نام فایل**: `project_dynamic_{نام_پروژه}_{تاریخ_و_زمان}.xlsx`

**شیت‌های موجود در فایل Static (16 شیت):**

**شیت‌های داده پایه (9 شیت):**
1. **Project**: اطلاعات کامل پروژه فعال
   - شامل: ID, نام, تاریخ‌ها (شمسی و میلادی), زیربنا, ضریب اصلاحی
2. **Units**: لیست کامل واحدها
   - شامل: ID واحد, شناسه پروژه, نام واحد, متراژ, قیمت هر متر, قیمت نهایی
3. **Investors**: لیست سرمایه‌گذاران
   - شامل: ID, نام و نام خانوادگی, تماس, ایمیل, نوع مشارکت, واحدهای متعلق (جدا شده با کاما), تاریخ قرارداد
4. **Periods**: لیست دوره‌های پروژه
   - شامل: ID, عنوان دوره, سال و ماه شمسی, وزن دوره, تاریخ شروع و پایان (شمسی و میلادی)
5. **InterestRates**: نرخ‌های سود
   - شامل: ID, نرخ سود روزانه, تاریخ اعمال, توضیحات, وضعیت فعال
6. **Transactions**: لیست کامل تراکنش‌ها
   - شامل: ID, شناسه و نام سرمایه‌گذار, شناسه و نام دوره, تاریخ (شمسی و میلادی), مبلغ, نوع تراکنش, روز مانده، روز از شروع
7. **Expenses**: لیست هزینه‌ها
   - شامل: ID, شناسه دوره, نوع هزینه, مبلغ, توضیحات
8. **Sales**: لیست فروش/مرجوعی‌ها
   - شامل: ID, شناسه دوره, مبلغ, توضیحات
9. **UserProfiles**: پروفایل کاربران
   - شامل: ID, نام کاربری, نقش، شماره تلفن، بخش

**شیت‌های محاسباتی (6 شیت):**
1. **Dashboard**: خلاصه کلی پروژه
   - اطلاعات واحدها (تعداد، متراژ، ارزش)
   - اطلاعات مالی (سرمایه موجود، سود، موجودی، هزینه‌ها، مانده صندوق)
   - اطلاعات سرمایه‌گذاران (تعداد کل، تعداد مالکان)
2. **Profit_Metrics**: محاسبات سود
   - درصد سود کل، سالانه، ماهانه، روزانه
   - دوره متوسط ساخت، ضریب اصلاحی
3. **Cost_Metrics**: محاسبات هزینه
   - هزینه‌های کل و نهایی
   - هزینه هر متر (خالص و ناخالص)
   - سود نهایی و درصد سود
4. **Investor_Analysis**: تحلیل تفصیلی سرمایه‌گذاران
   - برای هر سرمایه‌گذار: آورده، برداشت، سرمایه خالص، سود، نسبت‌ها، شاخص نفع
5. **Period_Summary**: خلاصه دوره‌ای
   - برای هر دوره: آورده، برداشت، سرمایه، سود، هزینه، فروش، مانده صندوق
   - مقادیر تجمعی برای هر فاکتور
   - ردیف جمع کل
6. **Transaction_Summary**: خلاصه تراکنش‌ها
   - تعداد کل تراکنش‌ها
   - مجموع آورده‌ها، برداشت‌ها، سودها
   - سرمایه موجود

**ویژگی‌های فایل Excel:**
- پشتیبانی کامل از زبان فارسی (فونت Tahoma)
- فرمت‌بندی اعداد با جداکننده هزارگان
- هدرهای رنگی و استایل‌دار برای خوانایی بهتر
- عرض ستون‌ها به صورت خودکار تنظیم می‌شود
- هر دو تاریخ شمسی و میلادی نمایش داده می‌شود
- همه محاسبات در سرور انجام شده (Static - بدون فرمول)

**مثال استفاده:**
```bash
# دانلود فایل Excel
curl -O -J http://localhost:8000/api/v1/Project/export_excel/

# یا در مرورگر
http://localhost:8000/api/v1/Project/export_excel/
```

**نکات مهم:**
- نیاز به احراز هویت دارد
- فقط پروژه فعال export می‌شود
- فایل به صورت attachment دانلود می‌شود
- نام فایل شامل نام پروژه و تاریخ/زمان تولید است

**شیت‌های موجود در فایل Dynamic (15 شیت):**

**شیت‌های ویژه:**
1. **📋 فهرست**: فهرست کامل شیت‌ها با لینک
2. **📖 راهنمای فرمول‌ها**: توضیح کامل Named Ranges و فرمول‌ها

**شیت‌های داده پایه (9 شیت):**
- همان شیت‌های Static (بدون تغییر)
- قابل ویرایش توسط کاربر
- شامل فریز و فیلتر خودکار

**شیت‌های محاسباتی (4 شیت):**
1. **Dashboard_Dynamic**: خلاصه کلی با فرمول
2. **Profit_Metrics_Dynamic**: محاسبات سود با فرمول
3. **Cost_Metrics_Dynamic**: محاسبات هزینه با فرمول
4. **Transaction_Summary_Dynamic**: خلاصه تراکنش‌ها با فرمول

**Named Ranges (14 مورد):**
- `TransactionAmounts`: مبالغ تراکنش‌ها
- `TransactionTypes`: انواع تراکنش
- `TransactionInvestors`: ID سرمایه‌گذاران
- `TransactionPeriods`: ID دوره‌ها
- `ExpenseAmounts`: مبالغ هزینه‌ها
- `SaleAmounts`: مبالغ فروش
- `UnitAreas`: متراژ واحدها
- `UnitPrices`: قیمت واحدها
- `TotalDeposits`: جمع آورده
- `TotalWithdrawals`: جمع برداشت
- `TotalCapital`: سرمایه کل
- `TotalProfit`: سود کل
- `TotalExpenses`: هزینه کل
- `TotalSales`: فروش کل

**ویژگی‌های فایل Dynamic:**
- ✅ فرمول‌های Excel قابل مشاهده
- ✅ محاسبات خودکار با تغییر داده‌ها
- ✅ Named Ranges برای خوانایی
- ✅ شیت راهنما برای آموزش
- ✅ داده‌های پایه قابل ویرایش
- ✅ فریز و فیلتر روی شیت‌های داده

**مثال استفاده:**
```bash
# دانلود فایل Static
curl -O -J http://localhost:8000/api/v1/Project/export_excel_static/

# دانلود فایل Dynamic
curl -O -J http://localhost:8000/api/v1/Project/export_excel_dynamic/
```

**برنامه آینده:**
- **فاز سوم**: فایل ترکیبی با هر دو نوع محاسبات (static + dynamic)

---

### 👥 **Investor APIs**

#### 1. آمار تفصیلی سرمایه‌گذار
- **Endpoint**: `GET /api/v1/Investor/{id}/detailed_statistics/`
- **توضیح**: آمار کامل سرمایه‌گذار
- **پاسخ شامل**:
  - اطلاعات سرمایه‌گذار
  - `total_principal`: آورده کل
  - `total_withdrawal`: برداشت کل
  - `total_profit`: سود کل
  - `net_principal`: سرمایه خالص
  - `total_balance`: موجودی کل
  - نسخه‌های تومان

#### 2. نسبت‌های سرمایه‌گذار
- **Endpoint**: `GET /api/v1/Investor/{id}/ratios/`
- **توضیح**: محاسبه نسبت‌های سرمایه‌گذار
- **پاسخ شامل**:
  - `capital_ratio`: نسبت سرمایه فرد به کل
  - `profit_ratio`: نسبت سود فرد به کل
  - `total_ratio`: نسبت کل فرد به کل
  - `profit_index`: شاخص نفع
  - نسخه‌های فرمت شده

#### 3. خلاصه تمام سرمایه‌گذاران
- **Endpoint**: `GET /api/v1/Investor/all_investors_summary/`
- **توضیح**: آمار تمام سرمایه‌گذاران
- **پاسخ شامل**: لیست آمار تمام سرمایه‌گذاران

---

### 💳 **Transaction APIs**

#### 1. آمار تفصیلی تراکنش‌ها
- **Endpoint**: `GET /api/v1/Transaction/detailed_statistics/`
- **توضیح**: آمار تراکنش‌ها با فیلترهای پیشرفته
- **پارامترهای اختیاری**:
  - `project_id`: شناسه پروژه
  - `investor_id`: شناسه سرمایه‌گذار
  - `date_from`: تاریخ شروع
  - `date_to`: تاریخ پایان
  - `transaction_type`: نوع تراکنش
- **پاسخ شامل**:
  - `total_transactions`: تعداد کل تراکنش‌ها
  - `total_deposits`: مجموع واریزها
  - `total_withdrawals`: مجموع برداشت‌ها
  - `total_profits`: مجموع سودها
  - `net_capital`: سرمایه موجود
  - نسخه‌های فرمت شده

> پیاده‌سازی سرور از مرجع واحد `Transaction.objects.totals(project, filters)` استفاده می‌کند تا سازگاری با SSOT حفظ شود.

---

### 📅 **Period APIs**

#### 1. داده‌های نمودار دوره‌ای
- **Endpoint**: `GET /api/v1/Period/chart_data/`
- **توضیح**: دریافت داده‌های دوره‌ای برای نمودارها
- **پاسخ شامل**:
  - `period_id`: شناسه دوره
  - `period_label`: عنوان دوره
  - `year`: سال شمسی
  - `month_number`: شماره ماه
  - `capital`: سرمایه دوره (آورده + برداشت)
  - `expenses`: هزینه‌های دوره
  - `sales`: فروش/مرجوعی دوره
  - `fund_balance`: مانده صندوق
  - `cumulative_capital`: سرمایه تجمعی
  - `cumulative_expenses`: هزینه تجمعی
  - `cumulative_sales`: فروش تجمعی

#### 2. خلاصه کامل دوره‌ای (جدید)
- **Endpoint**: `GET /api/v1/Period/period_summary/`
- **توضیح**: دریافت خلاصه کامل دوره‌ای شامل تمام فاکتورها و مقادیر تجمعی
- **پاسخ شامل**:
  - **برای هر دوره**:
    - `period_id`: شناسه دوره
    - `period_label`: عنوان دوره
    - `year`: سال شمسی
    - `month_number`: شماره ماه
    - `month_name`: نام ماه
    - `weight`: وزن دوره
    - **فاکتورهای دوره**:
      - `deposits`: آورده دوره (شامل `principal_deposit` و `loan_deposit`)
      - `withdrawals`: برداشت دوره (منفی)
      - `net_capital`: سرمایه خالص (آورده + برداشت)
      - `profits`: سود دوره
      - `expenses`: هزینه‌های دوره
      - `sales`: فروش/مرجوعی دوره
      - `fund_balance`: مانده صندوق
    - **مقادیر تجمعی**:
      - `cumulative_deposits`: آورده تجمعی
      - `cumulative_withdrawals`: برداشت تجمعی
      - `cumulative_net_capital`: سرمایه تجمعی
      - `cumulative_profits`: سود تجمعی
      - `cumulative_expenses`: هزینه تجمعی
      - `cumulative_sales`: فروش تجمعی
      - `cumulative_fund_balance`: مانده تجمعی
  - **خلاصه کلی (totals)**:
    - `total_deposits`: مجموع آورده
    - `total_withdrawals`: مجموع برداشت
    - `total_net_capital`: سرمایه خالص کل
    - `total_profits`: مجموع سود
    - `total_expenses`: مجموع هزینه‌ها
    - `total_sales`: مجموع فروش
    - `final_fund_balance`: مانده صندوق نهایی
    - `total_periods`: تعداد دوره‌ها

**نکات مهم**:
1. مقدار `withdrawals` در دیتابیس منفی است، بنابراین `net_capital = deposits + withdrawals`
2. نوع تراکنش سود `profit_accrual` است (نه `profit_payment`)
3. محاسبات تراکنش‌ها از Manager سفارشی `Transaction.objects` انجام می‌شود تا یکپارچگی حفظ شود.

---

## 🔍 **راه‌های بررسی محاسبات موجود**

### 1. **بررسی مستند**
- فایل `docs/FINANCIAL_CALCULATIONS.md` شامل تمام محاسبات
- هر محاسبه دارای نام، فرمول، مکان استفاده و نوع داده

### 2. **بررسی API Reference**
- این فایل شامل تمام API های موجود
- هر API دارای توضیح کامل و فیلدهای پاسخ

### 3. **بررسی کد سرویس**
- فایل `construction/calculations.py` شامل تمام کلاس‌های محاسباتی
- هر کلاس دارای متدهای مختلف

### 4. **بررسی JavaScript Service**
- فایل `static/js/financial-calculations.js` شامل تمام توابع
- هر تابع دارای توضیح و مثال استفاده

---

## 🚀 **نحوه استفاده**

### 1. **استفاده مستقیم از API**
```javascript
// دریافت متریک‌های سود
const profitMetrics = await fetch('/api/v1/Project/profit_metrics/');
const data = await profitMetrics.json();
```

### 2. **استفاده از سرویس JavaScript**
```javascript
// استفاده از سرویس محاسبات مالی
const profitMetrics = await window.financialService.getProfitMetrics();
```

### 3. **استفاده از توابع کمکی**
```javascript
// استفاده از توابع کمکی
const analysis = await window.loadProjectData();
```

---

## 📝 **نکات مهم**

1. **کش**: تمام API ها دارای کش 30 ثانیه‌ای هستند
2. **Fallback**: در صورت خطا، کدهای قدیمی اجرا می‌شوند
3. **پارامترها**: تمام API ها پارامتر `project_id` اختیاری دارند
4. **فرمت**: تمام اعداد با فرمت مناسب برگردانده می‌شوند

---

## 🔄 **به‌روزرسانی**

این فایل باید هر بار که API جدیدی اضافه می‌شود به‌روزرسانی شود.

---

**تاریخ ایجاد**: 2025-01-04  
**نسخه**: 1.0  
**وضعیت**: در حال توسعه

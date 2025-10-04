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

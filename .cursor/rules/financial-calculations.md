# 📊 قانون محاسبات مالی پروژه

## 🎯 هدف
این قانون نحوه استفاده از محاسبات مالی در پروژه را تعریف می‌کند. تمام محاسبات مالی باید از سمت سرور انجام شوند و کلاینت فقط نتایج را نمایش دهد.

---

## 🚫 **قوانین ممنوع**

### ❌ **محاسبات در JavaScript ممنوع است**
- هرگز محاسبات مالی پیچیده در JavaScript انجام ندهید
- از فرمول‌های ریاضی در کلاینت خودداری کنید
- محاسبات تکراری در صفحات مختلف ممنوع است

### ❌ **کدهای تکراری ممنوع است**
- هر محاسبه فقط یک بار در سمت سرور پیاده‌سازی شود
- از کپی کردن فرمول‌ها در صفحات مختلف خودداری کنید

---

## ✅ **قوانین اجباری**

### 1. **استفاده از سرویس محاسبات مالی**
```javascript
// ✅ درست - استفاده از سرویس
const profitMetrics = await window.financialService.getProfitMetrics();
const costMetrics = await window.financialService.getCostMetrics();

// ❌ اشتباه - محاسبه در JavaScript
const profit = (totalValue - totalCost) / totalCost * 100;
```

### 2. **استفاده از API های موجود**
```javascript
// ✅ درست - استفاده از API
const response = await fetch('/api/v1/Project/profit_metrics/');
const data = await response.json();

// ❌ اشتباه - محاسبه محلی
const calculateProfit = () => { /* محاسبات پیچیده */ };
```

### 3. **استفاده از توابع کمکی**
### 4. **مرجع واحد تراکنش‌ها (اجباری)**
- هرگونه محاسبه برای آورده/برداشت/سرمایه خالص باید فقط از طریق Manager سفارشی مدل تراکنش انجام شود: `Transaction.objects`.
- از توابع زیر استفاده کنید و Query پراکنده ننویسید:
  - `project_totals(project=None)`
  - `period_totals(project, period)`
  - `cumulative_until(project, upto_period)`
- استاندارد: `deposits = principal_deposit + loan_deposit`، `withdrawals = principal_withdrawal` (منفی)، `net_capital = deposits + withdrawals`.

### 5. **قانون مرجع واحد محاسبات (SSOT - سراسری)**
- همه محاسبات سمت سرور باید از «یک مرجع واحد» فراخوانی شوند؛ از ایجاد چند تابع/ماژول با منطق مشابه برای یک محاسبه خودداری کنید.
- مرجع‌های کنونی:
  - تراکنش‌ها: `Transaction.objects` (Manager سفارشی) برای deposits/withdrawals/net_capital و مشتقات.
  - متریک‌های هزینه/ارزش/سود: سرویس‌های `construction/calculations.py` مانند `ProjectCalculations`, `ProfitCalculations`.
- هرگاه نیاز به محاسبه جدید است، ابتدا بررسی کنید آیا در این مراجع قابل بیان/گسترش است؛ در صورت امکان همان‌جا اضافه کنید (نه در فایل‌ها/توابع دیگر).
- هدف: حذف تعارض‌های محاسباتی، کاهش تکرار، سهولت تغییر قوانین، و تست‌پذیری بهتر.

```javascript
// ✅ درست - استفاده از توابع کمکی
const analysis = await window.loadProjectData();
const investorData = await window.loadInvestorData(investorId);

// ❌ اشتباه - پیاده‌سازی مجدد
const fetchData = async () => { /* کد تکراری */ };
```

---

## 📋 **فهرست محاسبات موجود**

### 🏗️ **محاسبات پروژه (5 محاسبه)**
- ✅ سرمایه موجود (Current Capital)
- ✅ سود کل (Total Profit)
- ✅ موجودی کل (Grand Total)
- ✅ تعداد روزهای فعال (Active Days)
- ✅ مدت پروژه (Project Duration)

### 💰 **محاسبات هزینه و فروش (6 محاسبه)**
- ✅ هزینه نهایی (Final Cost)
- ✅ هزینه هر متر خالص (Net Cost Per Meter)
- ✅ هزینه هر متر ناخالص (Gross Cost Per Meter)
- ✅ ارزش هر متر (Value Per Meter)
- ✅ سود نهایی (Final Profit Amount)
- ✅ درصد سود کل (Total Profit Percentage)

### 📈 **محاسبات سود زمانی (4 محاسبه)**
- ✅ دوره متوسط ساخت (Average Construction Period)
- ✅ درصد سود سالانه (Annual Profit Percentage)
- ✅ درصد سود ماهانه (Monthly Profit Percentage)
- ✅ درصد سود روزانه (Daily Profit Percentage)

### 👥 **محاسبات سرمایه‌گذاران (8 محاسبه)**
- ✅ آورده کل (Total Principal)
- ✅ برداشت کل (Total Withdrawal)
- ✅ سرمایه خالص (Net Principal)
- ✅ موجودی کل سرمایه‌گذار (Total Balance)
- ✅ نسبت سرمایه فرد به کل (Capital Ratio)
- ✅ نسبت سود فرد به کل (Profit Ratio to Total)
- ✅ نسبت کل فرد به کل (Total Ratio to Grand Total)
- ✅ شاخص نفع (Profit Index)

### 📊 **محاسبات تراکنش‌ها (4 محاسبه)**
- ✅ مجموع واریزها (Total Deposits)
- ✅ مجموع برداشت‌ها (Total Withdrawals)
- ✅ مجموع سودها (Total Profits)
- ✅ سرمایه موجود (Net Capital)

### 🏗️ **محاسبات ساخت و ساز (5 محاسبه)**
- ✅ تعداد واحدها (Total Units)
- ✅ متراژ کل (Total Area)
- ✅ قیمت کل (Total Value)
- ✅ زیربنای کل (Total Infrastructure)
- ✅ ضریب اصلاحی (Correction Factor)

### 📅 **محاسبات زمانی (2 محاسبه)**
- ✅ مدت پروژه (Project Duration)
- ✅ روزهای فعال (Active Days)

### 📅 **محاسبات دوره‌ای (14 محاسبه)**
- ✅ آورده دوره (Period Deposits)
- ✅ برداشت دوره (Period Withdrawals)
- ✅ سرمایه خالص دوره (Period Net Capital)
- ✅ سود دوره (Period Profits)
- ✅ هزینه‌های دوره (Period Expenses)
- ✅ فروش دوره (Period Sales)
- ✅ مانده صندوق دوره (Period Fund Balance)
- ✅ آورده تجمعی (Cumulative Deposits)
- ✅ برداشت تجمعی (Cumulative Withdrawals)
- ✅ سرمایه تجمعی (Cumulative Net Capital)
- ✅ سود تجمعی (Cumulative Profits)
- ✅ هزینه تجمعی (Cumulative Expenses)
- ✅ فروش تجمعی (Cumulative Sales)
- ✅ مانده تجمعی (Cumulative Fund Balance)

### 💱 **محاسبات تبدیل واحد (4 محاسبه)**
- ✅ تبدیل به تومان (Convert to Toman)
- ✅ فرمت اعداد (Format Numbers)
- ✅ فرمت درصد (Format Percentage)
- ✅ تبدیل به کلمات فارسی (Convert to Persian Words)

### 📈 **محاسبات آماری (3 محاسبه)**
- ✅ میانگین (Average)
- ✅ مجموع تجمعی (Cumulative Sum)
- ✅ تعداد منحصر به فرد (Unique Count)

### 🎯 **محاسبات خاص (3 محاسبه)**
- ✅ نرخ سود فعلی (Current Interest Rate)
- ✅ تعداد مالکان (Owner Count)
- ✅ تعداد سرمایه‌گذاران (Investor Count)

---

## 🌐 **API های موجود**

### **Project APIs**
1. `GET /api/v1/Project/comprehensive_analysis/` - تحلیل جامع
2. `GET /api/v1/Project/profit_metrics/` - متریک‌های سود
3. `GET /api/v1/Project/cost_metrics/` - متریک‌های هزینه
4. `GET /api/v1/Project/project_statistics_detailed/` - آمار تفصیلی

### **Investor APIs**
1. `GET /api/v1/Investor/{id}/detailed_statistics/` - آمار تفصیلی
2. `GET /api/v1/Investor/{id}/ratios/` - نسبت‌ها
3. `GET /api/v1/Investor/all_investors_summary/` - خلاصه همه

### **Transaction APIs**
1. `GET /api/v1/Transaction/detailed_statistics/` - آمار تفصیلی

### **Period APIs**
1. `GET /api/v1/Period/chart_data/` - داده‌های نمودار دوره‌ای
2. `GET /api/v1/Period/period_summary/` - خلاصه کامل دوره‌ای (شامل تمام فاکتورها و مقادیر تجمعی)

---

## 🔍 **نحوه بررسی محاسبات موجود**

### 1. **بررسی فایل‌های مستندات**
- `docs/FINANCIAL_CALCULATIONS.md` - مستند کامل 52 محاسبه
- `docs/API_REFERENCE.md` - مرجع API های موجود
- `docs/IMPLEMENTED_CALCULATIONS.md` - فهرست محاسبات پیاده‌سازی شده

### 2. **اجرای اسکریپت بررسی**
```bash
python3 scripts/check_calculations.py
```

### 3. **بررسی کد سرویس**
- `construction/calculations.py` - کلاس‌های محاسباتی
- `static/js/financial-calculations.js` - سرویس JavaScript

---

## 🚀 **الگوهای استفاده**

### **الگوی 1: دریافت تحلیل جامع**
```javascript
// برای دریافت تمام آمار پروژه
const analysis = await window.financialService.getComprehensiveAnalysis();
if (analysis.error) {
    console.error('خطا در دریافت تحلیل:', analysis.error);
    return;
}

// استفاده از داده‌ها
const projectInfo = analysis.project_info;
const costMetrics = analysis.cost_metrics;
const profitMetrics = analysis.profit_percentages;
```

### **الگوی 2: دریافت متریک‌های خاص**
```javascript
// برای دریافت متریک‌های سود
const profitMetrics = await window.financialService.getProfitMetrics();
if (profitMetrics.error) {
    console.error('خطا در دریافت متریک‌های سود:', profitMetrics.error);
    return;
}

// استفاده از داده‌ها
const totalProfitPercentage = profitMetrics.total_profit_percentage;
const annualProfitPercentage = profitMetrics.annual_profit_percentage;
```

### **الگوی 3: دریافت آمار سرمایه‌گذار**
```javascript
// برای دریافت آمار سرمایه‌گذار
const investorData = await window.financialService.getInvestorStatistics(investorId);
if (investorData.error) {
    console.error('خطا در دریافت آمار سرمایه‌گذار:', investorData.error);
    return;
}

// استفاده از داده‌ها
const totalPrincipal = investorData.amounts.total_principal;
const totalProfit = investorData.amounts.total_profit;
```

### **الگوی 4: به‌روزرسانی UI**
```javascript
// برای به‌روزرسانی عناصر UI
const updates = [
    { id: 'totalProfitPercentage', value: profitMetrics.total_profit_percentage, formatter: (v) => `${v.toFixed(2)}%` },
    { id: 'annualProfitPercentage', value: profitMetrics.annual_profit_percentage, formatter: (v) => `${v.toFixed(2)}%` },
    { id: 'monthlyProfitPercentage', value: profitMetrics.monthly_profit_percentage, formatter: (v) => `${v.toFixed(2)}%` }
];

window.financialService.updateMultipleUI(updates);
```

---

## 📝 **نکات مهم**

### 1. **مدیریت خطا**
```javascript
try {
    const data = await window.financialService.getProfitMetrics();
    if (data.error) {
        console.error('خطا در API:', data.error);
        // fallback به روش قدیمی
        return;
    }
    // استفاده از داده‌ها
} catch (error) {
    console.error('خطا در درخواست:', error);
    // fallback به روش قدیمی
}
```

### 2. **کش و بهینه‌سازی**
- تمام API ها دارای کش 30 ثانیه‌ای هستند
- از درخواست‌های تکراری خودداری کنید
- از `window.financialService.clearCache()` برای پاک کردن کش استفاده کنید

### 3. **فرمت‌بندی**
```javascript
// استفاده از توابع فرمت‌بندی
const formattedNumber = window.financialService.formatNumber(1234567.89);
const formattedPercentage = window.financialService.formatPercentage(25.5);
const tomanAmount = window.financialService.convertToToman(1234567890);
```

---

## 🔄 **فرآیند اضافه کردن محاسبه جدید**

### 1. **بررسی وجود محاسبه**
- ابتدا بررسی کنید که آیا محاسبه در سمت سرور موجود است
- از اسکریپت `check_calculations.py` استفاده کنید

### 2. **اگر موجود نیست**
- محاسبه را در `construction/calculations.py` اضافه کنید
- API endpoint جدید ایجاد کنید
- سرویس JavaScript را به‌روزرسانی کنید
- مستندات را به‌روزرسانی کنید

### 3. **اگر موجود است**
- از API موجود استفاده کنید
- کد JavaScript جدید ننویسید

---

## ⚠️ **هشدارها**

### 1. **عدم رعایت قوانین**
- کدهای JavaScript که محاسبات مالی انجام دهند رد می‌شوند
- استفاده از فرمول‌های تکراری ممنوع است

### 2. **به‌روزرسانی مستندات**
- هر تغییر در محاسبات باید در مستندات منعکس شود
- فایل‌های قانون باید به‌روزرسانی شوند

### 3. **تست و اعتبارسنجی**
- تمام محاسبات جدید باید تست شوند
- از اسکریپت بررسی استفاده کنید

---

## 📚 **مراجع**

- `docs/FINANCIAL_CALCULATIONS.md` - مستند کامل محاسبات
- `docs/API_REFERENCE.md` - مرجع API ها
- `docs/IMPLEMENTED_CALCULATIONS.md` - فهرست محاسبات پیاده‌سازی شده
- `construction/calculations.py` - کد سرویس محاسبات
- `static/js/financial-calculations.js` - سرویس JavaScript

---

**تاریخ ایجاد**: 2025-01-04  
**نسخه**: 1.0  
**وضعیت**: فعال

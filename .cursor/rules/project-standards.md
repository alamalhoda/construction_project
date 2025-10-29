# 🏗️ قانون استانداردهای پروژه

## 🎯 هدف
این قانون استانداردهای کلی پروژه را تعریف می‌کند که در تمام بخش‌ها باید رعایت شود.

---

## 🚫 **قوانین ممنوع**

### ❌ **محاسبات مالی در JavaScript ممنوع است**
- تمام محاسبات مالی باید در سمت سرور انجام شوند
- از فرمول‌های ریاضی پیچیده در کلاینت خودداری کنید

### ❌ **کدهای تکراری ممنوع است**
- هر محاسبه فقط یک بار در سمت سرور پیاده‌سازی شود
- از کپی کردن کد در صفحات مختلف خودداری کنید

### ❌ **رنگ‌های hard-coded ممنوع است**
- از CSS Variables استفاده کنید
- رنگ‌های استاندارد پروژه را رعایت کنید

---

## ✅ **قوانین اجباری**

### 1. **استفاده از سرویس محاسبات مالی**
```javascript
// ✅ درست
const profitMetrics = await window.financialService.getProfitMetrics();

// ❌ اشتباه
const profit = (totalValue - totalCost) / totalCost * 100;
```

### 2. **استفاده از رنگ‌های استاندارد**
```css
/* ✅ درست */
color: var(--profit-color);
background-color: var(--profit-color-light);

/* ❌ اشتباه */
color: #21ba45;
background-color: green;
```

### 3. **فرمت اعداد استاندارد**
```javascript
// ✅ درست - فرمت انگلیسی با جداکننده هزارگان
const formatted = new Intl.NumberFormat('en-US').format(1234567);

// ❌ اشتباه - فرمت فارسی یا بدون جداکننده
const formatted = "1,234,567"; // فارسی
```

### 4. **شامل کردن Copyright Notice**
```html
<!-- ✅ درست - در تمام صفحات -->
<footer class="footer">
    <div class="container">
        <div class="row">
            <div class="col-12 text-center">
                <p class="mb-0">
                    © 2024 
                    <a href="https://royasoftteam.ir" target="_blank" class="text-decoration-none">
                        <i class="fas fa-code"></i> RoyaSoftTeam
                    </a>
                </p>
            </div>
        </div>
    </div>
</footer>
```

---

## 📊 **استانداردهای محاسبات**

### **استفاده از API های موجود:**
1. `GET /api/v1/Project/comprehensive_analysis/` - تحلیل جامع
2. `GET /api/v1/Project/profit_metrics/` - متریک‌های سود
3. `GET /api/v1/Project/cost_metrics/` - متریک‌های هزینه
4. `GET /api/v1/Investor/{id}/detailed_statistics/` - آمار سرمایه‌گذار
5. `GET /api/v1/Transaction/detailed_statistics/` - آمار تراکنش‌ها

### **استفاده از سرویس JavaScript:**
```javascript
// دریافت تحلیل جامع
const analysis = await window.financialService.getComprehensiveAnalysis();

// دریافت متریک‌های سود
const profitMetrics = await window.financialService.getProfitMetrics();

// دریافت متریک‌های هزینه
const costMetrics = await window.financialService.getCostMetrics();

// دریافت آمار سرمایه‌گذار
const investorData = await window.financialService.getInvestorStatistics(investorId);
```

---

## 🎨 **استانداردهای رنگ‌بندی**

### **رنگ‌های استاندارد:**
- 🔵 آبی (#2185d0) - آورده و واریزی
- 🔴 قرمز (#db2828) - برداشت و خروجی  
- 🟢 سبز (#21ba45) - سود مشارکت و درآمد
- 🟣 بنفش (#aa26ff) - سرمایه موجود و موجودی
- 🔴 قرمز تیره (#dc3545) - هزینه‌ها و خرجی
- 🟡 زرد (#ffc107) - فروش/مرجوعی
- ⚫ خاکستری (#6c757d) - مانده صندوق، مجموع و کل
- 🟡 طلایی (#ffd700) - شاخص نفع و عملکرد برتر

### **استفاده از CSS Variables:**
```css
:root {
    --deposit-color: #2185d0;           /* آبی - آورده و واریزی */
    --withdrawal-color: #db2828;        /* قرمز - برداشت و خروجی */
    --profit-color: #21ba45;            /* سبز - سود مشارکت و درآمد */
    --capital-color: #aa26ff;           /* بنفش - سرمایه موجود و موجودی */
    --expense-color: #dc3545;           /* قرمز تیره - هزینه‌ها و خرجی */
    --refund-color: #ffc107;            /* زرد - فروش/مرجوعی */
    --balance-color: #6c757d;           /* خاکستری - مانده صندوق */
    --total-color: #6c757d;             /* خاکستری - مجموع و کل */
    --gold-color: #ffd700;              /* طلایی - شاخص نفع و عملکرد برتر */
}
```

> **📖 مرجع کامل**: برای جزئیات بیشتر به فایل `.cursor/rules/color-standards-complete.md` مراجعه کنید.

---

## 📝 **استانداردهای کدنویسی**

### 1. **نام‌گذاری متغیرها**
```javascript
// ✅ درست - نام‌های معنادار
const totalProfitPercentage = profitMetrics.total_profit_percentage;
const annualProfitPercentage = profitMetrics.annual_profit_percentage;

// ❌ اشتباه - نام‌های غیرمعنادار
const a = profitMetrics.total_profit_percentage;
const b = profitMetrics.annual_profit_percentage;
```

### 2. **مدیریت خطا**
```javascript
// ✅ درست - مدیریت خطا
try {
    const data = await window.financialService.getProfitMetrics();
    if (data.error) {
        console.error('خطا در API:', data.error);
        return;
    }
    // استفاده از داده‌ها
} catch (error) {
    console.error('خطا در درخواست:', error);
    // fallback
}
```

### 3. **فرمت‌بندی اعداد**
```javascript
// ✅ درست - فرمت استاندارد
const formatNumber = (num) => {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(num);
};

const formatPercentage = (num) => {
    return `${formatNumber(num)}%`;
};
```

---

## 🔍 **فرآیند بررسی**

### 1. **بررسی محاسبات موجود**
```bash
# اجرای اسکریپت بررسی
python3 scripts/check_calculations.py
```

### 2. **بررسی مستندات**
- `docs/FINANCIAL_CALCULATIONS.md` - مستند کامل محاسبات
- `docs/API_REFERENCE.md` - مرجع API ها
- `docs/IMPLEMENTED_CALCULATIONS.md` - فهرست محاسبات پیاده‌سازی شده

### 3. **بررسی کد**
- `construction/calculations.py` - کلاس‌های محاسباتی
- `static/js/financial-calculations.js` - سرویس JavaScript

---

## 🚀 **الگوهای استفاده**

### **الگوی 1: بارگذاری داده‌های پروژه**
```javascript
async function loadProjectData() {
    try {
        const analysis = await window.financialService.getComprehensiveAnalysis();
        if (analysis.error) {
            console.error('خطا در دریافت تحلیل:', analysis.error);
            return null;
        }
        return analysis;
    } catch (error) {
        console.error('خطا در بارگذاری داده‌ها:', error);
        return null;
    }
}
```

### **الگوی 2: به‌روزرسانی UI**
```javascript
function updateUI(data) {
    const updates = [
        { id: 'totalProfitPercentage', value: data.total_profit_percentage, formatter: (v) => `${v.toFixed(2)}%` },
        { id: 'annualProfitPercentage', value: data.annual_profit_percentage, formatter: (v) => `${v.toFixed(2)}%` },
        { id: 'monthlyProfitPercentage', value: data.monthly_profit_percentage, formatter: (v) => `${v.toFixed(2)}%` }
    ];
    
    window.financialService.updateMultipleUI(updates);
}
```

### **الگوی 3: مدیریت خطا و Fallback**
```javascript
async function loadDataWithFallback() {
    try {
        // تلاش برای استفاده از API جدید
        const data = await window.financialService.getProfitMetrics();
        if (data.error) {
            throw new Error(data.error);
        }
        return data;
    } catch (error) {
        console.warn('API جدید در دسترس نیست، استفاده از روش قدیمی:', error);
        // fallback به روش قدیمی
        return await loadDataLegacy();
    }
}
```

---

## ⚠️ **هشدارها**

### 1. **عدم رعایت قوانین**
- کدهای JavaScript که محاسبات مالی انجام دهند رد می‌شوند
- استفاده از رنگ‌های hard-coded ممنوع است
- کدهای تکراری پذیرفته نمی‌شوند

### 2. **به‌روزرسانی مستندات**
- هر تغییر در محاسبات باید در مستندات منعکس شود
- فایل‌های قانون باید به‌روزرسانی شوند

### 3. **تست و اعتبارسنجی**
- تمام محاسبات جدید باید تست شوند
- از اسکریپت بررسی استفاده کنید

---

## 📚 **مراجع**

### **فایل‌های قانون:**
- `.cursor/rules/financial-calculations.md` - قانون محاسبات مالی
- `.cursor/rules/color-standards-complete.md` - قانون کامل رنگ‌بندی

### **مستندات:**
- `docs/FINANCIAL_CALCULATIONS.md` - مستند کامل محاسبات
- `docs/API_REFERENCE.md` - مرجع API ها
- `docs/IMPLEMENTED_CALCULATIONS.md` - فهرست محاسبات پیاده‌سازی شده

### **کد:**
- `construction/calculations.py` - سرویس محاسبات
- `static/js/financial-calculations.js` - سرویس JavaScript

---

**تاریخ ایجاد**: 2025-01-04  
**نسخه**: 1.0  
**وضعیت**: فعال

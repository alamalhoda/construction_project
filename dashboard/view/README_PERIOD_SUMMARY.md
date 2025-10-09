# 📅 صفحه خلاصه دوره‌ای پروژه

## 🎯 هدف
صفحه خلاصه دوره‌ای برای نمایش جامع تمام فاکتورهای مالی در هر دوره زمانی طراحی شده است. این صفحه به کاربران امکان می‌دهد روند مالی پروژه را در طول زمان مشاهده و تحلیل کنند.

---

## 📍 مسیر دسترسی

### مسیر مستقیم:
```
/dashboard/period-summary/
```

### از داشبورد کاربری:
1. ورود به سیستم
2. داشبورد کاربری → کارت "خلاصه دوره‌ای"

---

## 🔌 API Endpoint

### Endpoint:
```
GET /construction/api/v1/Period/period_summary/
```

### پاسخ:
```json
{
  "success": true,
  "data": [
    {
      "period_id": 1,
      "period_label": "مرداد 1402",
      "year": 1402,
      "month_number": 5,
      "month_name": "مرداد",
      "weight": 37,
      
      // فاکتورهای دوره
      "deposits": 24945000000.0,
      "withdrawals": -700000000.0,
      "net_capital": 24245000000.0,
      "profits": 0.0,
      "expenses": 27824500000.0,
      "sales": 0.0,
      "fund_balance": -3579500000.0,
      
      // مقادیر تجمعی
      "cumulative_deposits": 24945000000.0,
      "cumulative_withdrawals": -700000000.0,
      "cumulative_net_capital": 24245000000.0,
      "cumulative_profits": 0.0,
      "cumulative_expenses": 27824500000.0,
      "cumulative_sales": 0.0,
      "cumulative_fund_balance": -3579500000.0
    }
  ],
  "totals": {
    "total_deposits": 102836765466.5,
    "total_withdrawals": -11961000000.0,
    "total_net_capital": 90875765466.5,
    "total_profits": 0.0,
    "total_expenses": 55461513310.0,
    "total_sales": 3309700200.0,
    "final_fund_balance": 38723952356.5,
    "total_periods": 37
  },
  "active_project": "نام پروژه"
}
```

---

## 📊 محاسبات

### فاکتورهای هر دوره:

1. **آورده (deposits)**
   - فرمول: `SUM(amount) WHERE transaction_type = 'principal_deposit'`
   - واحد: تومان

2. **برداشت (withdrawals)**
   - فرمول: `SUM(amount) WHERE transaction_type = 'principal_withdrawal'`
   - واحد: تومان
   - ⚠️ **نکته**: در دیتابیس منفی است

3. **سرمایه خالص (net_capital)**
   - فرمول: `deposits + withdrawals`
   - واحد: تومان
   - ⚠️ **نکته مهم**: چون withdrawals منفی است، از جمع استفاده می‌کنیم نه تفریق

4. **سود (profits)**
   - فرمول: `SUM(amount) WHERE transaction_type = 'profit_accrual'`
   - واحد: تومان
   - ⚠️ **نکته**: نوع تراکنش سود `profit_accrual` است نه `profit_payment`

5. **هزینه‌ها (expenses)**
   - فرمول: `SUM(amount) FROM Expense WHERE period = period_id`
   - واحد: تومان

6. **فروش (sales)**
   - فرمول: `SUM(amount) FROM Sale WHERE period = period_id`
   - واحد: تومان

7. **مانده صندوق (fund_balance)**
   - فرمول: `cumulative_net_capital - cumulative_expenses + cumulative_sales`
   - واحد: تومان

### مقادیر تجمعی:

تمام مقادیر بالا به صورت تجمعی (cumulative) نیز محاسبه می‌شوند:
- `cumulative_deposits = SUM(deposits از دوره اول تا دوره فعلی)`
- `cumulative_withdrawals = SUM(withdrawals از دوره اول تا دوره فعلی)`
- و غیره...

---

## 🎨 ویژگی‌های صفحه

### 1️⃣ **کارت‌های آماری (8 کارت)**
- مجموع آورده
- مجموع برداشت
- سرمایه خالص کل
- مجموع سود
- مجموع هزینه‌ها
- مجموع فروش/مرجوعی
- مانده صندوق نهایی
- تعداد دوره‌ها

### 2️⃣ **جدول کامل دوره‌ای**
- نمایش فاکتورهای هر دوره
- نمایش مقادیر تجمعی (قابل نمایش/مخفی کردن)
- رنگ‌بندی استاندارد پروژه
- فرمت عددی انگلیسی با جداکننده

### 3️⃣ **دکمه نمایش/مخفی کردن ستون‌های تجمعی**
- امکان نمایش یا مخفی کردن ستون‌های تجمعی
- بهبود خوانایی جدول

### 3️⃣ **دکمه خروجی Excel**
- دانلود جدول دوره‌ای به صورت فایل Excel
- شامل جدول کامل با تمام داده‌های دوره‌ها
- شامل تمام ستون‌های دوره و ستون‌های تجمعی (17 ستون)
- نام فایل: `خلاصه_دوره‌ای_[تاریخ].xlsx`

### 4️⃣ **نوار ناوبری**
- دسترسی سریع به سایر صفحات
- داشبورد اصلی
- داشبورد پروژه
- داشبورد هزینه‌ها
- مدیریت تراکنش‌ها

---

## 🎨 رنگ‌بندی استاندارد

| مفهوم | رنگ | کد رنگ |
|-------|-----|---------|
| آورده | آبی | `#2185d0` |
| برداشت | قرمز | `#db2828` |
| سود | سبز | `#21ba45` |
| سرمایه خالص | بنفش | `#aa26ff` |
| هزینه | قرمز تیره | `#dc3545` |
| فروش | زرد | `#ffc107` |
| مانده صندوق | خاکستری | `#6c757d` |

---

## 📱 واکنش‌گرا (Responsive)

صفحه برای نمایش در اندازه‌های مختلف صفحه نمایش بهینه شده است:

- **دسکتاپ**: جدول کامل با تمام ستون‌ها
- **تبلت**: جدول با scroll افقی
- **موبایل**: کارت‌های آماری یک ستونی، جدول با scroll افقی

---

## 🔧 فایل‌های مرتبط

### Backend:
- `construction/api.py` (خطوط 648-777): endpoint `period_summary`
- `construction/api.py` (خطوط 563-646): endpoint `chart_data`
- `construction/serializers.py`: `PeriodSerializer`
- `construction/models.py`: مدل `Period`

### Frontend:
- `dashboard/view/period_summary.html`: صفحه HTML کامل
- `dashboard/views.py` (خطوط 186-195): view `period_summary`
- `dashboard/urls.py` (خط 14): URL mapping

### Dashboard:
- `dashboard/view/user_dashboard.html`: کارت دسترسی به صفحه

### مستندات:
- `docs/API_REFERENCE.md`: مرجع کامل API
- `docs/IMPLEMENTED_CALCULATIONS.md`: فهرست محاسبات
- `.cursor/rules/financial-calculations.md`: قوانین محاسبات

---

## 📝 نکات مهم

### ⚠️ نکته بسیار مهم درباره برداشت:
```python
# مقدار withdrawals در دیتابیس منفی است
withdrawals = -700000000.0  # منفی

# بنابراین برای محاسبه سرمایه خالص:
net_capital = deposits + withdrawals
# مثال: 24945000000 + (-700000000) = 24245000000 ✅

# ❌ اشتباه:
net_capital = deposits - withdrawals
# مثال: 24945000000 - (-700000000) = 25645000000 ❌
```

### فرمت اعداد:
- تمام اعداد با فرمت انگلیسی و جداکننده سه رقمی نمایش داده می‌شوند
- برداشت‌ها با مقدار مطلق (بدون علامت منفی) نمایش داده می‌شوند

### مدیریت خطا:
- در صورت عدم وجود پروژه فعال، پیام خطا نمایش داده می‌شود
- در صورت خطا در API، پیام خطای مناسب نمایش داده می‌شود

---

## 🚀 نحوه استفاده در کد

### JavaScript:
```javascript
// دریافت خلاصه دوره‌ای
async function loadPeriodSummary() {
    try {
        const response = await fetch('/construction/api/v1/Period/period_summary/');
        const result = await response.json();
        
        if (result.success) {
            console.log('تعداد دوره‌ها:', result.totals.total_periods);
            console.log('مجموع آورده:', result.totals.total_deposits);
            console.log('سرمایه خالص:', result.totals.total_net_capital);
            
            // پردازش داده‌های هر دوره
            result.data.forEach(period => {
                console.log(`${period.period_label}: ${period.net_capital}`);
            });
        }
    } catch (error) {
        console.error('خطا در دریافت داده‌ها:', error);
    }
}
```

### Python (در Views دیگر):
```python
from construction import models
from django.db.models import Sum

def get_period_summary():
    active_project = models.Project.get_active_project()
    periods = models.Period.objects.filter(
        project=active_project
    ).order_by('year', 'month_number')
    
    for period in periods:
        transactions = models.Transaction.objects.filter(
            project=active_project,
            period=period
        )
        
        deposits = transactions.filter(
            transaction_type='principal_deposit'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        withdrawals = transactions.filter(
            transaction_type='principal_withdrawal'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        profits = transactions.filter(
            transaction_type='profit_accrual'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # توجه: withdrawals منفی است
        net_capital = deposits + withdrawals
```

---

## 🔄 به‌روزرسانی و نگهداری

### هنگام اضافه کردن فاکتور مالی جدید:
1. به‌روزرسانی endpoint `period_summary` در `construction/api.py`
2. اضافه کردن ستون جدید به جدول در `period_summary.html`
3. اضافه کردن کارت آماری (در صورت نیاز)
4. به‌روزرسانی مستندات

### هنگام تغییر در ساختار دوره:
1. به‌روزرسانی مدل `Period`
2. به‌روزرسانی `PeriodSerializer`
3. به‌روزرسانی endpoint‌ها
4. به‌روزرسانی صفحه HTML

---

## 📚 مراجع

- [API Reference](../../docs/API_REFERENCE.md)
- [Financial Calculations](../../docs/FINANCIAL_CALCULATIONS.md)
- [Implemented Calculations](../../docs/IMPLEMENTED_CALCULATIONS.md)
- [Financial Calculations Rules](../../.cursor/rules/financial-calculations.md)

---

**تاریخ ایجاد**: 2025-01-08  
**نسخه**: 1.0  
**وضعیت**: فعال و آماده استفاده

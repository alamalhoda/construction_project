# 📊 مرجع سریع Excel Dynamic

## 🚀 شروع سریع

### تولید فایل
```bash
# از Management Command
python manage.py export_excel --dynamic

# یا از API
GET /api/v1/Project/export_excel_dynamic/
```

---

## 📋 شیت‌های کلیدی

| شیت | هدف | نوع |
|-----|-----|-----|
| `Comprehensive_Metrics` | قلب سیستم - همه محاسبات | محاسباتی ⭐⭐⭐ |
| `Transaction_Profit_Calculations` | محاسبه سود تراکنش‌ها | محاسباتی ⭐⭐ |
| `PeriodExpenseSummary` | دوره متوسط ساخت | کمکی ⭐ |
| `Transactions` | تراکنش‌های مالی | پایه |
| `📖 راهنمای فرمول‌ها` | راهنمای کامل | راهنما |

---

## 🏷️ Named Ranges مهم

### مالی
```
TotalCapital           → سرمایه موجود
TotalProfit            → سود تراکنش‌ها
BuildingProfit         → سود نهایی ساختمان
TotalExpenses          → هزینه کل
NetCost                → هزینه خالص
```

### زمانی
```
AverageConstructionPeriod  → دوره متوسط ساخت (ماه)
AnnualProfitPercentage     → درصد سود سالانه
MonthlyProfitPercentage    → درصد سود ماهانه
DailyProfitPercentage      → درصد سود روزانه
```

### محاسبه سود
```
CalculatedTotalProfit  → جمع سود محاسبه شده
```

---

## 🧮 فرمول‌های کلیدی

### دوره متوسط ساخت
```excel
=SUMPRODUCT(PeriodExpenseSummary!C:C, PeriodExpenseSummary!D:D) / SUM(PeriodExpenseSummary!C:C)
```

### سود تراکنش
```excel
=مبلغ × (نرخ_سود_روزانه / 100) × روز_مانده
```

### درصد سود سالانه
```excel
=IF(AverageConstructionPeriod=0, 0, (TotalProfitPercentage/AverageConstructionPeriod)*12)
```

---

## 📊 ستون‌های مهم Transactions

| ستون | عنوان | استفاده |
|------|--------|---------|
| A | ID | شناسه یکتا |
| C | شناسه سرمایه‌گذار | برای فیلتر |
| E | شناسه دوره | برای گروه‌بندی |
| I | مبلغ | محاسبات مالی |
| J | نوع تراکنش | آورده/برداشت/سود |
| L | روز مانده | محاسبه سود ⭐ |

---

## 🔧 عملیات رایج

### اضافه کردن Named Range
```python
NamedRangeHelper.create_named_range(
    workbook, 
    'MyRange',           # نام
    'Sheet_Name',        # شیت
    '$B$5'              # سلول (absolute)
)
```

### استفاده از VLOOKUP
```excel
=VLOOKUP(A3, Transactions!$A:$L, 12, FALSE)
```
- `A3`: مقدار جستجو
- `$A:$L`: محدوده
- `12`: شماره ستون
- `FALSE`: تطابق دقیق

### جمع با شرط
```excel
=SUMIF(TransactionTypes, "آورده", TransactionAmounts)
```

---

## ⚠️ نکات مهم

1. **ترتیب شیت‌ها**: شیت‌های پایه قبل از محاسباتی
2. **Absolute References**: همیشه `$B$5` نه `B5`
3. **Named Ranges**: قبل از استفاده تعریف شوند
4. **دو نوع سود**: 
   - `TotalProfit`: سود پرداختی
   - `BuildingProfit`: سود محاسبه شده
5. **VLOOKUP**: برای ردیف‌های نامطابق

---

## 🐛 عیب‌یابی سریع

| خطا | علت | راه‌حل |
|-----|------|--------|
| #NAME? | Named Range نامعتبر | بررسی تعریف |
| #REF! | ارجاع نامعتبر | بررسی آدرس |
| #VALUE! | نوع داده اشتباه | استفاده از IF |
| #DIV/0! | تقسیم بر صفر | `IF(A1=0, 0, B1/A1)` |

---

## 📞 فایل‌های مرتبط

```
construction/excel_export_dynamic.py       # کد اصلی
DYNAMIC_EXCEL_DOCUMENTATION.md             # مستندات کامل
docs/API_REFERENCE.md                      # API
```

---

**نسخه**: 1.0.0 | **تاریخ**: دی 1403


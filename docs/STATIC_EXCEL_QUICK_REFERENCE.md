# 📊 مرجع سریع Excel Static

## 🚀 شروع سریع

### تولید فایل
```bash
# از Management Command
python manage.py export_excel
python manage.py export_excel --output report.xlsx

# یا از API
GET /construction/api/v1/Project/export_excel_static/
```

---

## 📋 شیت‌های کلیدی

| شیت | هدف | نوع |
|-----|-----|-----|
| `Dashboard` | نمای کلی پروژه | محاسباتی ⭐⭐⭐ |
| `Profit_Metrics` | محاسبات سود | محاسباتی ⭐⭐ |
| `Cost_Metrics` | محاسبات هزینه | محاسباتی ⭐⭐ |
| `Investor_Analysis` | تحلیل سرمایه‌گذاران | تحلیلی ⭐ |
| `Transactions` | تراکنش‌های مالی | پایه |
| `📋 فهرست` | فهرست شیت‌ها | راهنما |

---

## 🎨 رنگ‌های استاندارد

```
آبی (#2185d0)      → آورده
قرمز (#db2828)     → برداشت
سبز (#21ba45)      → سود
بنفش (#aa26ff)     → سرمایه موجود
قرمز تیره (#dc3545) → هزینه‌ها
زرد (#ffc107)      → فروش/مرجوعی
خاکستری (#6c757d)  → مانده صندوق
طلایی (#ffd700)    → شاخص نفع
```

---

## 🧮 محاسبات کلیدی

### دوره متوسط ساخت
```python
average_period = Σ(هزینه_دوره × وزن_دوره) / Σ(کل_هزینه‌ها)
```

### شاخص نفع
```python
profit_index = نسبت_سود / نسبت_سرمایه
```

### درصد سود سالانه
```python
annual_percentage = (total_profit_percentage / average_period) * 12
```

### هزینه خالص
```python
net_cost = total_expenses - total_sales
```

### سود نهایی
```python
final_profit = total_value - net_cost
```

---

## 📊 ستون‌های مهم

### Transactions
- **I**: مبلغ
- **J**: نوع تراکنش
- **L**: روز مانده

### Expenses
- **F**: مبلغ

### Sales
- **E**: مبلغ

### Periods
- **G**: وزن دوره ⭐

---

## 🔧 عملیات رایج

### اضافه کردن ستون
```python
headers.append('ستون جدید')
data.append(new_value)
```

### اعمال استایل
```python
ExcelStyleHelper.apply_header_style(cell)
ExcelStyleHelper.apply_cell_style(cell)
```

### تنظیمات شیت
```python
ExcelStyleHelper.freeze_header_row(ws)
ExcelStyleHelper.add_auto_filter(ws)
ExcelStyleHelper.auto_adjust_column_width(ws)
```

---

## ⚠️ نکات مهم

1. **محاسبات در سرور**: همه محاسبات در Python
2. **Timezone**: باید normalize شود
3. **Decimal to Float**: قبل از نوشتن تبدیل شود
4. **Select Related**: برای بهینه‌سازی
5. **رنگ‌بندی**: استاندارد پروژه رعایت شود

---

## 🐛 عیب‌یابی سریع

| مشکل | راه‌حل |
|------|--------|
| خطای Timezone | `normalize_datetime()` |
| فونت فارسی | استفاده از Tahoma |
| عرض ستون | `auto_adjust_column_width()` |
| حجم زیاد | محدود کردن داده‌ها |
| Memory Error | استفاده از `write_only=True` |

---

## 📞 فایل‌های مرتبط

```
construction/excel_export.py              # کد اصلی
construction/calculations.py              # محاسبات
STATIC_EXCEL_DOCUMENTATION.md             # مستندات کامل
```

---

**نسخه**: 1.0.0 | **تاریخ**: دی 1403


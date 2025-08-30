# 📁 Construction App Fixtures

این پوشه شامل فایل‌های ‏‍backup‏ دیتابیس پروژه ساخت است.

## 📋 فهرست فایل‌ها

### `complete_data_backup.json` (288KB)
- **تاریخ ایجاد**: 1403/06/09 02:17
- **محتوا**: همه داده‌های کامل پروژه ساخت
- **آمار داده‌ها**:
  - ✅ پروژه‌ها: 1
  - ✅ سرمایه‌گذاران: 16  
  - ✅ دوره‌ها: 37
  - ✅ تراکنش‌ها: 625 (با انواع تصحیح شده)
  - ✅ واحدها: 0
  - **کل**: 679 رکورد

## 🔄 نحوه استفاده

### ✅ بازیابی با اسکریپت (راحت‌ترین روش)
```bash
python scripts/restore_backup.py
```

### ✅ بازیابی دستی با Django
```bash
# پاک کردن داده‌های فعلی
python manage.py shell -c "
from construction.models import *
Transaction.objects.all().delete()
Period.objects.all().delete()
for investor in Investor.objects.all():
    investor.units.clear()
Investor.objects.all().delete()
Unit.objects.all().delete()
Project.objects.all().delete()
"

# بارگذاری backup
python manage.py loaddata construction/fixtures/complete_data_backup.json
```

## ⚠️ نکات مهم

1. **پشتیبان‌گیری جدید**:
   ```bash
   python manage.py dumpdata construction --indent 2 --output construction/fixtures/backup_$(date +%Y%m%d_%H%M).json
   ```

2. **این ‏‍backup‏ شامل داده‌های تصحیح شده است**:
   - انواع تراکنش‌ها طبق قوانین صحیح تنظیم شده‌اند
   - آورده (`principal_deposit`): فقط مثبت
   - خروج از سرمایه (`principal_withdrawal`): فقط منفی
   - سود (`profit_accrual`): مثبت و منفی

3. **قبل از بازیابی حتماً مطمئن شوید که نیاز دارید**!

## 📊 وضعیت انواع تراکنش در این ‏‍backup‏

- **آورده**: 253 تراکنش (همه مثبت)
- **سود**: 312 تراکنش (252 مثبت، 60 منفی)  
- **خروج از سرمایه**: 60 تراکنش (همه منفی)

این وضعیت کاملاً منطقی و تصحیح شده است. 🎯

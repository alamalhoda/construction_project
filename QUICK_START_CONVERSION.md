# راهنمای سریع تبدیل ریال به تومان

## 🚀 شروع سریع

### 1. تست عملکرد (توصیه می‌شود)
```bash
# فعال‌سازی محیط مجازی
source env/bin/activate

# تست عملکرد
python3 test_conversion.py

# تست تبدیل (بدون اعمال تغییرات)
python3 manage.py convert_rial_to_toman --dry-run
```

### 2. تبدیل واقعی
```bash
# تبدیل با بکاپ (برای سرور)
python3 manage.py convert_rial_to_toman --backup

# یا تبدیل مستقیم (برای تست محلی)
python3 manage.py convert_rial_to_toman
```

## 📁 فایل‌های ایجاد شده

- `construction/management/commands/convert_rial_to_toman.py` - دستور Django
- `scripts/convert_rial_to_toman.py` - اسکریپت Python ساده
- `scripts/convert_rial_to_toman.sh` - اسکریپت Bash
- `test_conversion.py` - اسکریپت تست
- `RIAL_TO_TOMAN_CONVERSION.md` - راهنمای کامل

## ⚡ دستورات سریع

```bash
# تست
source env/bin/activate && python3 test_conversion.py

# تست تبدیل
source env/bin/activate && python3 manage.py convert_rial_to_toman --dry-run

# تبدیل با بکاپ
source env/bin/activate && python3 manage.py convert_rial_to_toman --backup
```

## ⚠️ هشدار

**همیشه ابتدا تست کنید!** استفاده از `--dry-run` برای مشاهده تغییرات قبل از اعمال آنها ضروری است.

## 📊 آمار فعلی دیتابیس شما

بر اساس تست انجام شده:
- **🏠 واحدها**: 18 رکورد  
- **💳 تراکنش‌ها**: 630 رکورد
- **💸 هزینه‌ها**: 27 رکورد
- **🛒 فروش‌ها**: 2 رکورد

**🎯 مجموع**: 677 رکورد قابل تبدیل

## 💡 نمونه تبدیل

- **قیمت/متر**: 553,000,000 ریال → 55,300,000 تومان
- **قیمت کل**: 110,600,000,000 ریال → 11,060,000,000 تومان
- **مبلغ تراکنش**: 2,000,000,000 ریال → 200,000,000 تومان

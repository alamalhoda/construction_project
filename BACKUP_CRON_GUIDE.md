# راهنمای سیستم بک‌آپ خودکار (Cron)

## 📋 خلاصه

سیستم بک‌آپ خودکار با استفاده از **cron job** هر 6 ساعت یکبار بک‌آپ کامل از دیتابیس ایجاد می‌کند.

## 🔧 نصب و راه‌اندازی

### 1. فعال کردن Cron از طریق UI
```bash
# مراجعه به صفحه تنظیمات
http://localhost:8000/backup/settings/

# کلیک روی "فعال کردن Cron"
```

### 2. فعال کردن Cron از طریق خط فرمان
```bash
# اجرای اسکریپت تنظیم cron
./scripts/setup_cron.sh
```

### 3. بررسی وضعیت Cron
```bash
# مشاهده cron jobs فعال
crontab -l

# خروجی نمونه:
# 0 */6 * * * /Users/alamalhoda/Projects/Arash_Project/djangobuilder/construction_project/scripts/run_auto_backup.sh
```

## ⚙️ تنظیمات

### تغییر فاصله زمانی بک‌آپ

برای تغییر فاصله زمانی، فایل `scripts/setup_cron.sh` را ویرایش کنید:

```bash
# هر 6 ساعت (پیش‌فرض)
CRON_JOB="0 */6 * * * $BACKUP_SCRIPT"

# هر ساعت
CRON_JOB="0 * * * * $BACKUP_SCRIPT"

# هر 12 ساعت
CRON_JOB="0 */12 * * * $BACKUP_SCRIPT"

# هر روز در ساعت 2 صبح
CRON_JOB="0 2 * * * $BACKUP_SCRIPT"
```

### فرمت Cron
```
* * * * *
│ │ │ │ │
│ │ │ │ └─── روز هفته (0-7)
│ │ │ └───── ماه (1-12)
│ │ └─────── روز ماه (1-31)
│ └───────── ساعت (0-23)
└─────────── دقیقه (0-59)
```

## 🗂️ فایل‌های سیستم

### اسکریپت‌های اصلی
- `scripts/run_auto_backup.sh` - اسکریپت اجرای بک‌آپ
- `scripts/setup_cron.sh` - تنظیم cron job
- `scripts/remove_cron.sh` - حذف cron job

### Management Command
- `backup/management/commands/auto_backup.py` - Django command

### لاگ‌ها
- `logs/auto_backup.log` - لاگ اجرای بک‌آپ‌های خودکار

## 🔍 عیب‌یابی

### بررسی اجرای Cron
```bash
# بررسی لاگ سیستم cron
sudo tail -f /var/log/cron

# بررسی لاگ بک‌آپ
tail -f logs/auto_backup.log
```

### تست دستی
```bash
# اجرای دستی بک‌آپ خودکار
python manage.py auto_backup --force

# اجرای اسکریپت بک‌آپ
./scripts/run_auto_backup.sh
```

### مشکلات رایج

#### 1. Cron اجرا نمی‌شود
```bash
# بررسی مجوزهای فایل
ls -la scripts/run_auto_backup.sh

# باید خروجی مشابه زیر باشد:
# -rwxr-xr-x 1 user user 1234 Sep  2 21:00 scripts/run_auto_backup.sh
```

#### 2. مسیرهای اشتباه
```bash
# بررسی مسیرهای مطلق در اسکریپت
cat scripts/run_auto_backup.sh
```

#### 3. Virtual Environment
```bash
# اطمینان از فعال بودن virtual environment
source env/bin/activate
which python
```

## 🛠️ مدیریت

### غیرفعال کردن Cron
```bash
# از طریق UI
http://localhost:8000/backup/settings/ → "غیرفعال کردن Cron"

# از طریق خط فرمان
./scripts/remove_cron.sh
```

### ویرایش Cron Job
```bash
# ویرایش مستقیم crontab
crontab -e

# حذف خط مربوط به بک‌آپ و ذخیره
```

### پاک‌سازی لاگ‌ها
```bash
# پاک کردن لاگ قدیمی
> logs/auto_backup.log
```

## 📊 نظارت

### بررسی آمار بک‌آپ‌ها
```bash
# از طریق UI
http://localhost:8000/backup/list/

# از طریق خط فرمان
python manage.py shell
>>> from backup.models import BackupRecord
>>> BackupRecord.objects.filter(backup_type='automatic').count()
```

### بررسی حجم بک‌آپ‌ها
```bash
# حجم کل پوشه backups
du -sh backups/

# حجم هر بک‌آپ
du -sh backups/backup_*
```

## 🔒 امنیت

### مجوزهای فایل
```bash
# تنظیم مجوزهای مناسب
chmod 755 scripts/*.sh
chmod 644 logs/auto_backup.log
```

### پشتیبان‌گیری از Cron
```bash
# ذخیره تنظیمات cron فعلی
crontab -l > backup_cron.txt
```

## 📝 نکات مهم

1. **سرور باید روشن باشد** - Cron فقط زمانی کار می‌کند که سیستم روشن باشد
2. **Virtual Environment** - اسکریپت به صورت خودکار virtual environment را فعال می‌کند
3. **فضای دیسک** - اطمینان از وجود فضای کافی برای بک‌آپ‌ها
4. **پاک‌سازی خودکار** - سیستم به صورت خودکار بک‌آپ‌های قدیمی را حذف می‌کند

## 🆘 پشتیبانی

در صورت بروز مشکل:
1. بررسی لاگ‌ها
2. تست دستی اسکریپت‌ها
3. بررسی مجوزهای فایل‌ها
4. اطمینان از فعال بودن virtual environment

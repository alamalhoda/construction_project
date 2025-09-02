#!/bin/bash

# اسکریپت تنظیم cron برای بک‌آپ خودکار

PROJECT_DIR="/Users/alamalhoda/Projects/Arash_Project/djangobuilder/construction_project"
BACKUP_SCRIPT="$PROJECT_DIR/scripts/run_auto_backup.sh"

echo "🔧 تنظیم cron برای بک‌آپ خودکار..."
echo "📁 مسیر پروژه: $PROJECT_DIR"
echo "📜 اسکریپت بک‌آپ: $BACKUP_SCRIPT"

# بررسی وجود اسکریپت
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "❌ اسکریپت بک‌آپ یافت نشد: $BACKUP_SCRIPT"
    exit 1
fi

# ایجاد cron job برای هر 6 ساعت
CRON_JOB="0 */6 * * * $BACKUP_SCRIPT"

echo "⏰ Cron job پیشنهادی:"
echo "$CRON_JOB"
echo ""

# اضافه کردن به crontab
echo "📝 اضافه کردن به crontab..."

# بررسی وجود cron job قبلی
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo "⚠️ Cron job قبلاً وجود دارد"
    echo "🔄 حذف cron job قبلی..."
    crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT" | crontab -
fi

# اضافه کردن cron job جدید
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job با موفقیت اضافه شد"
    echo ""
    echo "📋 Cron jobs فعلی:"
    crontab -l
    echo ""
    echo "💡 برای حذف cron job از دستور زیر استفاده کنید:"
    echo "crontab -e"
    echo "و خط مربوط به بک‌آپ را حذف کنید"
else
    echo "❌ خطا در اضافه کردن cron job"
    exit 1
fi

#!/bin/bash

# اسکریپت حذف cron برای بک‌آپ خودکار

PROJECT_DIR="/Users/alamalhoda/Projects/Arash_Project/djangobuilder/construction_project"
BACKUP_SCRIPT="$PROJECT_DIR/scripts/run_auto_backup.sh"

echo "🗑️ حذف cron job بک‌آپ خودکار..."

# بررسی وجود cron job
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo "📝 حذف cron job..."
    crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT" | crontab -
    
    if [ $? -eq 0 ]; then
        echo "✅ Cron job با موفقیت حذف شد"
    else
        echo "❌ خطا در حذف cron job"
        exit 1
    fi
else
    echo "ℹ️ هیچ cron job بک‌آپ یافت نشد"
fi

echo ""
echo "📋 Cron jobs باقی‌مانده:"
crontab -l 2>/dev/null || echo "هیچ cron job وجود ندارد"

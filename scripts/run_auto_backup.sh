#!/bin/bash

# اسکریپت اجرای بک‌آپ خودکار
# این اسکریپت باید توسط cron اجرا شود

# مسیر پروژه
PROJECT_DIR="/Users/alamalhoda/Projects/Arash_Project/djangobuilder/construction_project"

# تغییر به مسیر پروژه
cd "$PROJECT_DIR"

# فعال‌سازی virtual environment
source env/bin/activate

# اجرای بک‌آپ خودکار
python manage.py auto_backup

# خروج از virtual environment
deactivate

# لاگ کردن نتیجه
echo "$(date): Auto backup completed" >> logs/auto_backup.log

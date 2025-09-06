#!/bin/bash

# Script برای راه‌اندازی پروژه در محیط Local Development
# Local Development Startup Script

echo "🚀 راه‌اندازی پروژه در محیط Local Development..."

# تنظیم متغیرهای محیطی
export DJANGO_ENVIRONMENT=development
export DB_NAME=database/local.sqlite3
export DEBUG=True

# فعال کردن virtual environment
source env/bin/activate

# اجرای migration ها (در صورت نیاز)
echo "📊 بررسی migration ها..."
python manage.py migrate

# راه‌اندازی سرور
echo "🌐 راه‌اندازی سرور Django..."
echo "📍 آدرس: http://127.0.0.1:8000"
echo "🔧 Admin: http://127.0.0.1:8000/admin/"
echo "📊 Dashboard: http://127.0.0.1:8000/construction/dashboard/"
echo "🔌 API: http://127.0.0.1:8000/api/construction/Investor/"
echo ""
echo "برای توقف سرور: Ctrl+C"
echo ""

python manage.py runserver 8000

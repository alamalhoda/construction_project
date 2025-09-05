#!/bin/bash
# اسکریپت راه‌اندازی خودکار برای GitHub Codespace
# Auto setup script for GitHub Codespace

echo "🚀 شروع راه‌اندازی پروژه Construction..."

# بررسی وجود virtual environment
if [ ! -d "venv" ]; then
    echo "📦 ایجاد virtual environment..."
    python3 -m venv venv
fi

# فعال‌سازی virtual environment
echo "🔧 فعال‌سازی virtual environment..."
source venv/bin/activate

# ایجاد پوشه‌های مورد نیاز
echo "📁 ایجاد پوشه‌های مورد نیاز..."
mkdir -p logs database media backups staticfiles

# کپی فایل محیط
echo "📋 کپی فایل محیط..."
cp .env.codespaces .env

# نصب dependencies
echo "📚 نصب dependencies..."
pip install -r requirements.txt

# اجرای migrations
echo "🗄️ اجرای migrations..."
python manage.py migrate

# جمع‌آوری static files
echo "📁 جمع‌آوری static files..."
python manage.py collectstatic --noinput

# ایجاد superuser (اختیاری)
echo "👤 بررسی superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superuser ایجاد شد')
else:
    print('ℹ️ Superuser قبلاً وجود دارد')
"

echo "✅ راه‌اندازی کامل شد!"
echo "🚀 شروع سرور Django..."

# اجرای سرور در background
nohup python manage.py runserver 0.0.0.0:8000 > /dev/null 2>&1 &
echo "✅ سرور Django روی پورت 8000 شروع شد!"

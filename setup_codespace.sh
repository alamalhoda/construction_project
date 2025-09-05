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

# Load کردن متغیرهای محیطی
echo "🔧 Load کردن متغیرهای محیطی..."
export $(cat .env | grep -v '^#' | xargs)

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

# بررسی فعال بودن virtual environment
echo "🔍 بررسی virtual environment..."
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ Virtual environment فعال است: $VIRTUAL_ENV"
else
    echo "⚠️ Virtual environment فعال نیست، فعال‌سازی مجدد..."
    . venv/bin/activate
    echo "✅ Virtual environment فعال شد: $VIRTUAL_ENV"
fi

# بررسی Python و Django
echo "🐍 بررسی Python و Django..."
python --version
python -c "import django; print(f'Django version: {django.get_version()}')"

# تاخیر برای اطمینان
echo "⏳ تاخیر 3 ثانیه برای اطمینان..."
sleep 3

# اجرای سرور در background با لاگ
echo "🚀 شروع سرور Django در background..."
nohup python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &
SERVER_PID=$!

# تاخیر برای شروع سرور
echo "⏳ تاخیر 5 ثانیه برای شروع سرور..."
sleep 5

# بررسی متغیرهای محیطی
echo "🔍 بررسی متغیرهای محیطی..."
echo "DB_NAME: $DB_NAME"
echo "USE_SQLITE: $USE_SQLITE"
echo "DJANGO_ENVIRONMENT: $DJANGO_ENVIRONMENT"
echo "CODESPACES: $CODESPACES"

# بررسی تنظیمات Django
echo "🔍 بررسی تنظیمات Django..."
python manage.py check_env

# بررسی وضعیت سرور
echo "🔍 بررسی وضعیت سرور..."
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ سرور Django با PID $SERVER_PID روی پورت 8000 شروع شد!"
    echo "📝 لاگ سرور در فایل server.log ذخیره می‌شود"
    echo "🌐 سرور در دسترس است: http://0.0.0.0:8000"
else
    echo "❌ خطا در شروع سرور! بررسی لاگ:"
    cat server.log
fi

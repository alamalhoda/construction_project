#!/bin/bash
# اسکریپت راه‌اندازی production برای GitHub Codespace
# Production setup script for GitHub Codespace

# فعال‌سازی دیباگ برای لاگ دقیق‌تر
set -x

echo "🚀 [PROD] شروع راه‌اندازی پروژه Construction... $(date)"

# تنظیم پرمیشن اسکریپت
chmod +x "$0"

# تنظیم متغیرهای محیطی برای Production
echo "🔧 [PROD] تنظیم متغیرهای محیطی برای Production... $(date)"
export DJANGO_ENVIRONMENT=production
export DJANGO_SETTINGS_MODULE=construction_project.production_settings

# بررسی وجود virtual environment
if [ ! -d "venv" ]; then
    echo "📦 [PROD] ایجاد virtual environment... $(date)"
    if ! python3 -m venv venv; then
        echo "❌ [PROD] خطا در ایجاد virtual environment!"
        exit 1
    fi
fi

# فعال‌سازی virtual environment
echo "🔧 [PROD] فعال‌سازی virtual environment... $(date)"
source venv/bin/activate

# بررسی فعال بودن virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ [PROD] Virtual environment فعال نشد!"
    exit 1
fi
echo "✅ [PROD] Virtual environment فعال است: $VIRTUAL_ENV"

# بررسی منابع سیستم
echo "📊 [PROD] بررسی منابع سیستم... $(date)"
free -m
nproc

# بررسی پیش‌نیازها
echo "🔍 [PROD] بررسی فایل‌های مورد نیاز... $(date)"
if [ ! -f requirements.txt ]; then
    echo "❌ [PROD] فایل requirements.txt پیدا نشد!"
    exit 1
fi
if [ ! -f .env.codespaces ]; then
    echo "⚠️ [PROD] فایل .env.codespaces پیدا نشد! لطفاً متغیرهای محیطی را دستی تنظیم کنید."
else
    echo "📋 [PROD] کپی فایل محیط codespaces..."
    cp .env.codespaces .env
fi

# Load کردن متغیرهای محیطی
if [ -f .env ]; then
    echo "🔧 [PROD] Load کردن متغیرهای محیطی... $(date)"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️ [PROD] فایل .env پیدا نشد!"
fi

# بررسی نسخه Python
echo "🐍 [PROD] بررسی نسخه Python... $(date)"
PYTHON_VERSION=$(python --version 2>&1)
if [[ ! $PYTHON_VERSION =~ "Python 3.8" && ! $PYTHON_VERSION =~ "Python 3.9" && ! $PYTHON_VERSION =~ "Python 3.10" && ! $PYTHON_VERSION =~ "Python 3.11" ]]; then
    echo "❌ [PROD] نسخه Python باید 3.8 یا بالاتر باشد! نسخه فعلی: $PYTHON_VERSION"
    exit 1
fi
echo "✅ [PROD] نسخه Python: $PYTHON_VERSION"

# نصب dependencies
echo "📚 [PROD] نصب dependencies... $(date)"
pip install --upgrade pip
if ! pip install -r requirements.txt --timeout=300; then
    echo "❌ [PROD] خطا در نصب dependencies!"
    exit 1
fi

# بررسی دسترسی به دیتابیس
echo "🗄️ [PROD] بررسی دسترسی به دیتابیس... $(date)"
if ! python manage.py check --database default; then
    echo "❌ [PROD] خطا در اتصال به دیتابیس!"
    exit 1
fi

# اجرای migrations
echo "🗄️ [PROD] اجرای migrations... $(date)"
if ! python manage.py migrate; then
    echo "❌ [PROD] خطا در اجرای migrations!"
    exit 1
fi

# جمع‌آوری static files
echo "📁 [PROD] جمع‌آوری static files... $(date)"
if ! python manage.py collectstatic --noinput; then
    echo "❌ [PROD] خطا در جمع‌آوری static files!"
    exit 1
fi

# بررسی superuser
echo "👤 [PROD] بررسی superuser... $(date)"
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    echo "👤 [PROD] ایجاد superuser خودکار..."
    python manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL"
else
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('⚠️ هیچ superuser وجود ندارد! لطفا دستی ایجاد کنید.')
else:
    print('ℹ️ حداقل یک superuser وجود دارد.')
"
fi

# اجرای تست‌ها (اختیاری)
echo "🧪 [PROD] اجرای تست‌های اصلی... $(date)"
if ! python manage.py test construction.tests.test_models construction.tests.test_views; then
    echo "⚠️ [PROD] برخی تست‌ها با خطا مواجه شدند! ادامه می‌دهیم اما لطفاً بررسی کنید."
fi

# بررسی پورت 8000
echo "🔍 [PROD] بررسی پورت 8000... $(date)"
if lsof -i:8000 > /dev/null; then
    echo "❌ [PROD] پورت 8000 در حال استفاده است!"
    exit 1
fi

# یادآوری برای SSL
echo "🔒 [PROD] توجه: برای Production، اطمینان حاصل کنید که SSL/HTTPS فعال است! $(date)"

# # تنظیم cron job برای پشتیبان‌گیری
# if [ -f scripts/setup_cron.sh ]; then
#     echo "⏰ [PROD] تنظیم cron job برای پشتیبان‌گیری خودکار... $(date)"
#     bash scripts/setup_cron.sh
# else
#     echo "⚠️ [PROD] اسکریپت setup_cron.sh پیدا نشد!"
# fi

# تنظیم log rotation (اختیاری - نیاز به sudo)
echo "📝 [PROD] تنظیم log rotation... $(date)"
if [ -w /etc/logrotate.d/ ]; then
    cat > /etc/logrotate.d/construction_project <<EOF
/workspaces/construction_project/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
EOF
    echo "✅ [PROD] Log rotation تنظیم شد"
else
    echo "⚠️ [PROD] دسترسی به /etc/logrotate.d/ نداریم - log rotation تنظیم نشد"
fi

# اجرای سرور با Gunicorn
echo "🚀 [PROD] اجرای سرور با Gunicorn... $(date)"

# متوقف کردن سرورهای قبلی
echo "🛑 [PROD] متوقف کردن سرورهای قبلی... $(date)"
pkill -f "python manage.py runserver" || true
pkill -f "gunicorn" || true
sleep 2

# اجرای Gunicorn در background
echo "🚀 [PROD] شروع Gunicorn... $(date)"
nohup venv/bin/gunicorn construction_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers $((2 * $(nproc) + 1)) \
    --timeout 120 \
    --graceful-timeout 120 \
    --access-logfile logs/gunicorn_access.log \
    --error-logfile logs/gunicorn_error.log \
    --log-level info \
    --preload \
    > logs/gunicorn_stdout.log 2>&1 &

GUNICORN_PID=$!
echo "✅ [PROD] Gunicorn با PID $GUNICORN_PID شروع شد"

sleep 5

# بررسی وضعیت Gunicorn
echo "🔍 [PROD] بررسی وضعیت Gunicorn... $(date)"
if ps -p $GUNICORN_PID > /dev/null; then
    echo "✅ [PROD] Gunicorn با موفقیت در حال اجرا است"
else
    echo "❌ [PROD] خطا در شروع Gunicorn! بررسی لاگ‌ها:"
    cat logs/gunicorn_error.log 2>/dev/null || echo "فایل لاگ یافت نشد"
    exit 1
fi

echo "📝 [PROD] لاگ‌ها:"
echo "  - logs/gunicorn_access.log"
echo "  - logs/gunicorn_error.log"
echo "  - logs/gunicorn_stdout.log"
echo "🌐 [PROD] سرور در دسترس است: http://localhost:8000"
echo "✅ [PROD] راه‌اندازی کامل شد! $(date)"
#!/bin/bash
# اسکریپت راه‌اندازی production برای GitHub Codespace
# Production setup script for GitHub Codespace

# فعال‌سازی دیباگ برای لاگ دقیق‌تر (غیرفعال برای خروجی تمیز)
# set -x

echo "🚀 [PROD] شروع راه‌اندازی پروژه Construction..."

# تنظیم پرمیشن اسکریپت
chmod +x "$0"

# تنظیم متغیرهای محیطی برای Production
echo "🔧 [PROD] تنظیم متغیرهای محیطی برای Production..."
export DJANGO_ENVIRONMENT=production
export DJANGO_SETTINGS_MODULE=construction_project.production_settings

# تنظیم timezone به تهران
echo "🕐 [PROD] تنظیم timezone به تهران..."
export TZ=Asia/Tehran
if command -v timedatectl > /dev/null 2>&1; then
    sudo timedatectl set-timezone Asia/Tehran > /dev/null 2>&1 || echo "⚠️ [PROD] نتوانستیم timezone سیستم را تغییر دهیم"
else
    echo "⚠️ [PROD] timedatectl در دسترس نیست - timezone فقط برای این session تنظیم شد"
fi

# بررسی وجود virtual environment
if [ ! -d "venv" ]; then
    echo "📦 [PROD] ایجاد virtual environment..."
    if ! python3 -m venv venv; then
        echo "❌ [PROD] خطا در ایجاد virtual environment!"
        exit 1
    fi
fi

# فعال‌سازی virtual environment
echo "🔧 [PROD] فعال‌سازی virtual environment..."
source venv/bin/activate

# بررسی فعال بودن virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ [PROD] Virtual environment فعال نشد!"
    exit 1
fi
echo "✅ [PROD] Virtual environment فعال است: $VIRTUAL_ENV"

# بررسی منابع سیستم (ساده)
echo "📊 [PROD] بررسی منابع سیستم..."
echo "💾 حافظه: $(free -h | awk '/^Mem:/ {print $3 "/" $2}') | 🖥️ CPU: $(nproc) cores"

# بررسی پیش‌نیازها
echo "🔍 [PROD] بررسی فایل‌های مورد نیاز..."
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
    echo "🔧 [PROD] Load کردن متغیرهای محیطی..."
    export $(cat .env | grep -v '^#' | xargs) > /dev/null 2>&1
else
    echo "⚠️ [PROD] فایل .env پیدا نشد!"
fi

# بررسی نسخه Python
echo "🐍 [PROD] بررسی نسخه Python..."
PYTHON_VERSION=$(python --version 2>&1)
if [[ ! $PYTHON_VERSION =~ "Python 3.8" && ! $PYTHON_VERSION =~ "Python 3.9" && ! $PYTHON_VERSION =~ "Python 3.10" && ! $PYTHON_VERSION =~ "Python 3.11" ]]; then
    echo "❌ [PROD] نسخه Python باید 3.8 یا بالاتر باشد! نسخه فعلی: $PYTHON_VERSION"
    exit 1
fi
echo "✅ [PROD] نسخه Python: $PYTHON_VERSION"

# نصب dependencies
echo "📚 [PROD] نصب dependencies..."
pip install --upgrade pip > /dev/null 2>&1
if ! pip install -r requirements.txt --timeout=300 --quiet; then
    echo "❌ [PROD] خطا در نصب dependencies!"
    exit 1
fi
echo "✅ [PROD] Dependencies نصب شدند"

# بررسی دسترسی به دیتابیس
echo "🗄️ [PROD] بررسی دسترسی به دیتابیس..."
if ! python manage.py check --database default > /dev/null 2>&1; then
    echo "❌ [PROD] خطا در اتصال به دیتابیس!"
    exit 1
fi

# اجرای migrations
echo "🗄️ [PROD] اجرای migrations..."
if ! python manage.py migrate > /dev/null 2>&1; then
    echo "❌ [PROD] خطا در اجرای migrations!"
    exit 1
fi

# جمع‌آوری static files با Whitenoise
echo "📁 [PROD] جمع‌آوری static files با Whitenoise..."
if ! python manage.py collectstatic --noinput > /dev/null 2>&1; then
    echo "❌ [PROD] خطا در جمع‌آوری static files!"
    exit 1
fi

# بررسی فایل‌های استاتیک
if [ -f "staticfiles/admin/css/base.css" ]; then
    echo "✅ [PROD] فایل‌های استاتیک Django Admin موجود است"
else
    echo "⚠️ [PROD] فایل‌های استاتیک Django Admin یافت نشد!"
fi

# بررسی timezone
echo "🕐 [PROD] بررسی تنظیمات timezone..."
python manage.py check_timezone

# بررسی superuser
echo "👤 [PROD] بررسی superuser..."
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    echo "👤 [PROD] ایجاد superuser خودکار..."
    python manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL" > /dev/null 2>&1
else
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('⚠️ هیچ superuser وجود ندارد! لطفا دستی ایجاد کنید.')
else:
    print('ℹ️ حداقل یک superuser وجود دارد.')
" > /dev/null 2>&1
fi

# اجرای تست‌ها (اختیاری)
# echo "🧪 [PROD] اجرای تست‌های اصلی... $(date)"
# if ! python manage.py test construction.tests.test_models construction.tests.test_views; then
#     echo "⚠️ [PROD] برخی تست‌ها با خطا مواجه شدند! ادامه می‌دهیم اما لطفاً بررسی کنید."
# fi

# بررسی پورت 8000
echo "🔍 [PROD] بررسی پورت 8000..."
if lsof -i:8000 > /dev/null 2>&1; then
    echo "❌ [PROD] پورت 8000 در حال استفاده است!"
    exit 1
fi

# # تنظیم cron job برای پشتیبان‌گیری
# if [ -f scripts/setup_cron.sh ]; then
#     echo "⏰ [PROD] تنظیم cron job برای پشتیبان‌گیری خودکار... $(date)"
#     bash scripts/setup_cron.sh
# else
#     echo "⚠️ [PROD] اسکریپت setup_cron.sh پیدا نشد!"
# fi

# تنظیم log rotation (اختیاری - نیاز به sudo)
echo "📝 [PROD] تنظیم log rotation..."
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
echo "🚀 [PROD] اجرای سرور با Gunicorn..."

# متوقف کردن سرورهای قبلی
echo "🛑 [PROD] متوقف کردن سرورهای قبلی..."
pkill -f "python manage.py runserver" > /dev/null 2>&1 || true
pkill -f "gunicorn" > /dev/null 2>&1 || true
sleep 2

# اجرای Gunicorn در background
echo "🚀 [PROD] شروع Gunicorn..."
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
echo "🔍 [PROD] بررسی وضعیت Gunicorn..."
if ps -p $GUNICORN_PID > /dev/null 2>&1; then
    echo "✅ [PROD] Gunicorn با موفقیت در حال اجرا است"
else
    echo "❌ [PROD] خطا در شروع Gunicorn! بررسی لاگ‌ها:"
    cat logs/gunicorn_error.log 2>/dev/null || echo "فایل لاگ یافت نشد"
    exit 1
fi
echo "🌐 [PROD] سرور در دسترس است: http://localhost:8000"
echo "✅ [PROD] راه‌اندازی کامل شد!"
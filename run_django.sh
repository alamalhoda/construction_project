#!/bin/bash

# اسکریپت اجرای دستورات Django با فعال‌سازی خودکار محیط مجازی
# استفاده: ./run_django.sh [دستورات Django]
# مثال: ./run_django.sh migrate construction

# بررسی وجود محیط مجازی
if [ ! -d "env" ]; then
    echo "❌ پوشه محیط مجازی (env) یافت نشد!"
    echo "لطفاً ابتدا محیط مجازی را ایجاد کنید:"
    echo "python3 -m venv env"
    exit 1
fi

# بررسی فعال بودن محیط مجازی
if [ -z "$VIRTUAL_ENV" ]; then
    echo "🔄 فعال‌سازی محیط مجازی..."
    source env/bin/activate
    echo "✅ محیط مجازی فعال شد"
else
    echo "✅ محیط مجازی قبلاً فعال است"
fi

# اجرای دستورات Django
echo "🚀 اجرای دستور: python3 manage.py $@"
python3 manage.py "$@"

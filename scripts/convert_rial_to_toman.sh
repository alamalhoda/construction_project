#!/bin/bash

# اسکریپت تبدیل ریال به تومان
# Script to convert Rial to Toman

echo "💰 اسکریپت تبدیل ریال به تومان"
echo "=================================="

# بررسی وجود محیط مجازی
if [ ! -d "env" ]; then
    echo "❌ محیط مجازی یافت نشد. لطفاً ابتدا محیط مجازی را فعال کنید."
    exit 1
fi

# فعال‌سازی محیط مجازی
source env/bin/activate

# بررسی پارامترها
case "$1" in
    "test")
        echo "🔍 اجرای تست (حالت آزمایشی)..."
        python3 manage.py convert_rial_to_toman --dry-run
        ;;
    "backup")
        echo "💾 ایجاد بکاپ و تبدیل..."
        python3 manage.py convert_rial_to_toman --backup
        ;;
    "convert")
        echo "⚡ تبدیل مستقیم (بدون بکاپ)..."
        python3 manage.py convert_rial_to_toman
        ;;
    *)
        echo "📖 راهنمای استفاده:"
        echo "  ./scripts/convert_rial_to_toman.sh test     # تست (حالت آزمایشی)"
        echo "  ./scripts/convert_rial_to_toman.sh backup   # بکاپ + تبدیل"
        echo "  ./scripts/convert_rial_to_toman.sh convert  # تبدیل مستقیم"
        echo ""
        echo "⚠️ توصیه: ابتدا با دستور 'test' تست کنید"
        ;;
esac

echo ""
echo "✅ اسکریپت تکمیل شد"

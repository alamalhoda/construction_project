#!/usr/bin/env python3
"""
اسکریپت ساده برای تبدیل ریال به تومان
Simple script to convert Rial to Toman
"""

import os
import sys
import django
from pathlib import Path

# اضافه کردن مسیر پروژه به sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')
django.setup()

from django.core.management import call_command

def main():
    """تابع اصلی برای اجرای تبدیل"""
    print("💰 اسکریپت تبدیل ریال به تومان")
    print("=" * 50)
    
    # بررسی حالت‌های مختلف
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            print("🔍 اجرای تست (حالت آزمایشی)...")
            call_command('convert_rial_to_toman', '--dry-run')
            
        elif command == "backup":
            print("💾 ایجاد بکاپ و تبدیل...")
            call_command('convert_rial_to_toman', '--backup')
            
        elif command == "convert":
            print("⚡ تبدیل مستقیم (بدون بکاپ)...")
            call_command('convert_rial_to_toman')
            
        else:
            print("❌ دستور نامعتبر")
            show_help()
    else:
        show_help()

def show_help():
    """نمایش راهنما"""
    print("\n📖 راهنمای استفاده:")
    print("  python3 scripts/convert_rial_to_toman.py test     # تست (حالت آزمایشی)")
    print("  python3 scripts/convert_rial_to_toman.py backup   # بکاپ + تبدیل")
    print("  python3 scripts/convert_rial_to_toman.py convert  # تبدیل مستقیم")
    print("\n⚠️ توصیه: ابتدا با دستور 'test' تست کنید")

if __name__ == "__main__":
    main()

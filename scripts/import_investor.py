#!/usr/bin/env python
"""
اسکریپت وارد کردن سرمایه‌گذاران از فایل CSV به دیتابیس Django

وارد کردن سرمایه‌گذاران از فایل CSV به دیتابیس Django
در پوشه temp_data فایلی به نام investors.csv وجود دارد که شامل سرمایه‌گذاران است.
این اسکریپت با دریافت این فایل و وارد کردن آنها به دیتابیس Django کار میکند.

برای استفاده از این اسکریپت، در ترمینال باید به پوشه پروژه وارد شوید و سپس اسکریپت را اجرا کنید.
construction_project git:(master) ✗ source env/bin/activate && python scripts/import_investor.py
"""

import os
import sys
import django
import csv
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# تنظیم متغیر محیطی Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')

# راه‌اندازی Django
django.setup()

from construction.models import Investor

# متغیر فایل ورودی - برای تغییر آسان فایل
CSV_FILE_PATH = project_root / 'temp_data' / 'investors.csv'


def parse_full_name(full_name):
    """
    تجزیه نام کامل به نام و نام خانوادگی
    """
    parts = full_name.strip().split()
    if len(parts) >= 2:
        first_name = parts[0]
        last_name = ' '.join(parts[1:])
    else:
        first_name = full_name.strip()
        last_name = ''
    
    return first_name, last_name


def import_investors_from_csv(csv_file_path):
    """
    وارد کردن سرمایه‌گذاران از فایل CSV
    """
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            created_count = 0
            updated_count = 0
            
            for row in csv_reader:
                full_name = row.get('name', '').strip()
                
                if not full_name:
                    print(f"نام خالی پیدا شد، ردیف نادیده گرفته شد: {row}")
                    continue
                
                # تجزیه نام کامل
                first_name, last_name = parse_full_name(full_name)
                
                # بررسی وجود سرمایه‌گذار
                investor, created = Investor.objects.get_or_create(
                    first_name=first_name,
                    last_name=last_name,
                    defaults={
                        'phone': '',  # فعلاً خالی
                        'email': '',  # فعلاً خالی
                    }
                )
                
                if created:
                    created_count += 1
                    print(f"سرمایه‌گذار جدید ایجاد شد: {investor}")
                else:
                    updated_count += 1
                    print(f"سرمایه‌گذار از قبل موجود بود: {investor}")
            
            print(f"\n=== خلاصه وارد کردن ===")
            print(f"تعداد سرمایه‌گذاران جدید: {created_count}")
            print(f"تعداد سرمایه‌گذاران موجود: {updated_count}")
            print(f"مجموع: {created_count + updated_count}")
            
    except FileNotFoundError:
        print(f"فایل پیدا نشد: {csv_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"خطا در وارد کردن داده‌ها: {e}")
        sys.exit(1)


def main():
    """
    تابع اصلی اسکریپت
    """
    print(f"شروع وارد کردن سرمایه‌گذاران از: {CSV_FILE_PATH}")
    
    # بررسی وجود فایل
    if not CSV_FILE_PATH.exists():
        print(f"فایل CSV موجود نیست: {CSV_FILE_PATH}")
        sys.exit(1)
    
    # نمایش تعداد رکوردهای موجود قبل از وارد کردن
    existing_count = Investor.objects.count()
    print(f"تعداد سرمایه‌گذاران موجود در دیتابیس: {existing_count}")
    
    # وارد کردن داده‌ها
    import_investors_from_csv(CSV_FILE_PATH)
    
    # نمایش تعداد نهایی
    final_count = Investor.objects.count()
    print(f"تعداد نهایی سرمایه‌گذاران در دیتابیس: {final_count}")


if __name__ == '__main__':
    main()

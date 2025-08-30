#!/usr/bin/env python
"""
اسکریپت وارد کردن دوره‌های زمانی از فایل CSV به دیتابیس Django

وارد کردن دوره‌های زمانی از فایل CSV به دیتابیس Django
در پوشه temp_data فایلی به نام periods.csv وجود دارد که شامل دوره‌های زمانی است.
این اسکریپت با دریافت این فایل و وارد کردن آنها به دیتابیس Django کار میکند.

برای استفاده از این اسکریپت، در ترمینال باید به پوشه پروژه وارد شوید و سپس اسکریپت را اجرا کنید.
construction_project git:(master) ✗ source env/bin/activate && python scripts/import_period.py
"""

import os
import sys
import django
import csv
from pathlib import Path
from datetime import date
from dateutil.relativedelta import relativedelta

# اضافه کردن مسیر پروژه به Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# تنظیم متغیر محیطی Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')

# راه‌اندازی Django
django.setup()

from construction.models import Project, Period

# متغیر فایل ورودی - برای تغییر آسان فایل
CSV_FILE_PATH = project_root / 'temp_data' / 'periods.csv'

# نام پروژه پیش‌فرض
DEFAULT_PROJECT_NAME = "پروژه اصلی"


def shamsi_to_gregorian(year, month):
    """
    تبدیل تاریخ شمسی به میلادی (تقریبی)
    این تابع تقریب زدنی است و برای محاسبات دقیق‌تر بهتر است از کتابخانه jdatetime استفاده شود
    """
    # تبدیل تقریبی سال شمسی به میلادی
    gregorian_year = year + 621
    
    # ماه‌های شمسی به میلادی (تقریبی)
    month_mapping = {
        1: (3, 21),   # فروردین -> مارس
        2: (4, 21),   # اردیبهشت -> آپریل  
        3: (5, 22),   # خرداد -> می
        4: (6, 22),   # تیر -> ژوئن
        5: (7, 23),   # مرداد -> ژوئیه
        6: (8, 23),   # شهریور -> آگوست
        7: (9, 23),   # مهر -> سپتامبر
        8: (10, 23),  # آبان -> اکتبر
        9: (11, 22),  # آذر -> نوامبر
        10: (12, 22), # دی -> دسامبر
        11: (1, 21),  # بهمن -> ژانویه (سال بعد)
        12: (2, 20),  # اسفند -> فوریه (سال بعد)
    }
    
    if month in [11, 12]:  # بهمن و اسفند
        gregorian_year += 1
    
    greg_month, greg_day = month_mapping.get(month, (1, 1))
    
    try:
        start_date = date(gregorian_year, greg_month, greg_day)
        # محاسبه تاریخ پایان (تقریباً 30 روز بعد)
        end_date = start_date + relativedelta(days=29)
        return start_date, end_date
    except ValueError:
        # در صورت خطا، تاریخ پیش‌فرض برگردانیم
        return date(gregorian_year, 1, 1), date(gregorian_year, 1, 30)


def get_or_create_default_project():
    """
    دریافت یا ایجاد پروژه پیش‌فرض
    """
    project, created = Project.objects.get_or_create(
        name=DEFAULT_PROJECT_NAME,
        defaults={
            'start_date_shamsi': date(1402, 5, 1),  # مرداد 1402
            'end_date_shamsi': date(1405, 5, 30),   # مرداد 1405
            'start_date_gregorian': date(2023, 7, 23),
            'end_date_gregorian': date(2026, 8, 21),
        }
    )
    
    if created:
        print(f"پروژه جدید ایجاد شد: {project.name}")
    else:
        print(f"از پروژه موجود استفاده می‌شود: {project.name}")
    
    return project


def import_periods_from_csv(csv_file_path):
    """
    وارد کردن دوره‌های زمانی از فایل CSV
    """
    try:
        # دریافت یا ایجاد پروژه پیش‌فرض
        project = get_or_create_default_project()
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            created_count = 0
            updated_count = 0
            
            for row in csv_reader:
                period_label = row.get('period_label', '').strip()
                year = int(row.get('year', 0))
                month_number = int(row.get('month_number', 0))
                month_name = row.get('month_name', '').strip()
                weight = int(row.get('weight', 0))
                
                if not period_label or not year or not month_number:
                    print(f"داده‌های ناقص، ردیف نادیده گرفته شد: {row}")
                    continue
                
                # محاسبه تاریخ‌های شمسی (تقریبی)
                # برای سادگی، از تاریخ‌های میلادی معادل استفاده می‌کنیم
                start_date_gregorian, end_date_gregorian = shamsi_to_gregorian(year, month_number)
                start_date_shamsi = start_date_gregorian  # فعلاً همان تاریخ میلادی
                end_date_shamsi = end_date_gregorian
                
                # تاریخ‌های میلادی از قبل محاسبه شده‌اند
                
                # بررسی وجود دوره
                period, created = Period.objects.get_or_create(
                    project=project,
                    year=year,
                    month_number=month_number,
                    defaults={
                        'label': period_label,
                        'month_name': month_name,
                        'weight': weight,
                        'start_date_shamsi': start_date_shamsi,
                        'end_date_shamsi': end_date_shamsi,
                        'start_date_gregorian': start_date_gregorian,
                        'end_date_gregorian': end_date_gregorian,
                    }
                )
                
                if created:
                    created_count += 1
                    print(f"دوره جدید ایجاد شد: {period}")
                else:
                    # به‌روزرسانی وزن اگر متفاوت باشد
                    if period.weight != weight:
                        period.weight = weight
                        period.save()
                        print(f"وزن دوره به‌روزرسانی شد: {period}")
                    updated_count += 1
                    print(f"دوره از قبل موجود بود: {period}")
            
            print(f"\n=== خلاصه وارد کردن ===")
            print(f"تعداد دوره‌های جدید: {created_count}")
            print(f"تعداد دوره‌های موجود: {updated_count}")
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
    print(f"شروع وارد کردن دوره‌ها از: {CSV_FILE_PATH}")
    
    # بررسی وجود فایل
    if not CSV_FILE_PATH.exists():
        print(f"فایل CSV موجود نیست: {CSV_FILE_PATH}")
        sys.exit(1)
    
    # نمایش تعداد رکوردهای موجود قبل از وارد کردن
    existing_count = Period.objects.count()
    print(f"تعداد دوره‌های موجود در دیتابیس: {existing_count}")
    
    # وارد کردن داده‌ها
    import_periods_from_csv(CSV_FILE_PATH)
    
    # نمایش تعداد نهایی
    final_count = Period.objects.count()
    print(f"تعداد نهایی دوره‌ها در دیتابیس: {final_count}")


if __name__ == '__main__':
    main()

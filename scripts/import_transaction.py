#!/usr/bin/env python
"""
اسکریپت وارد کردن تراکنش‌ها از فایل CSV به دیتابیس Django
"""

import os
import sys
import django
import csv
import jdatetime
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation

# اضافه کردن مسیر پروژه به Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# تنظیم متغیر محیطی Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')

# راه‌اندازی Django
django.setup()

from construction.models import Project, Investor, Period, Transaction

# متغیر فایل ورودی - برای تغییر آسان فایل
CSV_FILE_PATH = project_root / 'temp_data' / 'Transactions.csv'


def parse_shamsi_date(date_string):
    """
    تجزیه تاریخ شمسی از رشته (فرمت: 1402-05-16)
    """
    try:
        year, month, day = map(int, date_string.split('-'))
        return jdatetime.date(year, month, day)
    except (ValueError, AttributeError):
        return None


def parse_gregorian_date(date_string):
    """
    تجزیه تاریخ میلادی از رشته (فرمت: 2023-08-07)
    """
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except (ValueError, AttributeError):
        return None


def validate_date_conversion(shamsi_date_str, gregorian_date_str, row_index):
    """
    اعتبارسنجی تبدیل تاریخ شمسی به میلادی
    """
    # تجزیه تاریخ شمسی
    shamsi_date = parse_shamsi_date(shamsi_date_str)
    if not shamsi_date:
        print(f"⚠️  خطا در تجزیه تاریخ شمسی در ردیف {row_index}: {shamsi_date_str}")
        return None, None, False
    
    # تبدیل شمسی به میلادی
    converted_gregorian = shamsi_date.togregorian()
    
    # تجزیه تاریخ میلادی از فایل
    file_gregorian = parse_gregorian_date(gregorian_date_str)
    if not file_gregorian:
        print(f"⚠️  خطا در تجزیه تاریخ میلادی در ردیف {row_index}: {gregorian_date_str}")
        return shamsi_date, None, False
    
    # مقایسه تاریخ‌ها
    if converted_gregorian != file_gregorian:
        print(f"⚠️  عدم تطابق تاریخ‌ها در ردیف {row_index}:")
        print(f"    تاریخ شمسی: {shamsi_date_str} -> تبدیل شده: {converted_gregorian}")
        print(f"    تاریخ میلادی فایل: {file_gregorian}")
        return shamsi_date, file_gregorian, False
    
    return shamsi_date, file_gregorian, True


def get_or_create_project(project_name):
    """
    دریافت یا ایجاد پروژه
    """
    try:
        project = Project.objects.get(name=project_name)
        return project
    except Project.DoesNotExist:
        print(f"⚠️  پروژه با نام '{project_name}' یافت نشد. از پروژه پیش‌فرض استفاده می‌شود.")
        project, created = Project.objects.get_or_create(
            name="پروژه اصلی",
            defaults={
                'start_date_shamsi': jdatetime.date(1402, 5, 1).togregorian(),
                'end_date_shamsi': jdatetime.date(1405, 5, 30).togregorian(),
                'start_date_gregorian': jdatetime.date(1402, 5, 1).togregorian(),
                'end_date_gregorian': jdatetime.date(1405, 5, 30).togregorian(),
            }
        )
        return project


def get_investor_by_name(full_name):
    """
    یافتن سرمایه‌گذار بر اساس نام کامل
    """
    parts = full_name.strip().split()
    if len(parts) >= 2:
        first_name = parts[0]
        last_name = ' '.join(parts[1:])
    else:
        first_name = full_name.strip()
        last_name = ''
    
    try:
        investor = Investor.objects.get(first_name=first_name, last_name=last_name)
        return investor
    except Investor.DoesNotExist:
        print(f"⚠️  سرمایه‌گذار '{full_name}' یافت نشد.")
        return None


def get_period_by_label(project, period_label):
    """
    یافتن دوره بر اساس عنوان
    """
    try:
        period = Period.objects.get(project=project, label=period_label)
        return period
    except Period.DoesNotExist:
        print(f"⚠️  دوره '{period_label}' برای پروژه '{project.name}' یافت نشد.")
        return None


def import_transactions_from_csv(csv_file_path):
    """
    وارد کردن تراکنش‌ها از فایل CSV
    """
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            created_count = 0
            skipped_count = 0
            error_count = 0
            date_mismatch_count = 0
            
            for row_num, row in enumerate(csv_reader, start=2):  # شروع از ردیف 2 (بعد از header)
                try:
                    # استخراج داده‌ها از CSV
                    project_id = row.get('project_id', '').strip()
                    period_label = row.get('period_label', '').strip()
                    date_shamsi_str = row.get('date_shamsi', '').strip()
                    date_gregorian_str = row.get('date_gregorian', '').strip()
                    investor_name = row.get('investor_name', '').strip()
                    entry_type = row.get('entry_type', '').strip()
                    amount_str = row.get('amount', '').strip()
                    day_remaining_str = row.get('day_remaining', '').strip()
                    day_from_start_str = row.get('day_from_start', '').strip()
                    
                    # بررسی داده‌های ضروری
                    if not all([project_id, period_label, date_shamsi_str, date_gregorian_str, 
                               investor_name, entry_type, amount_str]):
                        print(f"⚠️  داده‌های ناقص در ردیف {row_num}, نادیده گرفته شد")
                        skipped_count += 1
                        continue
                    
                    # اعتبارسنجی تاریخ‌ها
                    shamsi_date, gregorian_date, date_valid = validate_date_conversion(
                        date_shamsi_str, date_gregorian_str, row_num
                    )
                    
                    if not shamsi_date or not gregorian_date:
                        error_count += 1
                        continue
                    
                    if not date_valid:
                        date_mismatch_count += 1
                        # ادامه پردازش با تاریخ فایل
                    
                    # دریافت پروژه
                    project = get_or_create_project(project_id)
                    
                    # دریافت سرمایه‌گذار
                    investor = get_investor_by_name(investor_name)
                    if not investor:
                        error_count += 1
                        continue
                    
                    # دریافت دوره
                    period = get_period_by_label(project, period_label)
                    if not period:
                        error_count += 1
                        continue
                    
                    # تبدیل مبلغ
                    try:
                        amount = Decimal(amount_str)
                    except (InvalidOperation, ValueError):
                        print(f"⚠️  خطا در تبدیل مبلغ در ردیف {row_num}: {amount_str}")
                        error_count += 1
                        continue
                    
                    # تبدیل day_remaining و day_from_start
                    try:
                        day_remaining = int(day_remaining_str) if day_remaining_str else 0
                        day_from_start = int(day_from_start_str) if day_from_start_str else 0
                    except ValueError:
                        print(f"⚠️  خطا در تبدیل روزها در ردیف {row_num}")
                        day_remaining = 0
                        day_from_start = 0
                    
                    # ایجاد تراکنش
                    transaction = Transaction.objects.create(
                        project=project,
                        investor=investor,
                        period=period,
                        date_shamsi=shamsi_date,
                        date_gregorian=gregorian_date,
                        amount=amount,
                        transaction_type=entry_type,
                        description=f"وارد شده از فایل CSV - ردیف {row_num}",
                        day_remaining=day_remaining,
                        day_from_start=day_from_start,
                    )
                    
                    created_count += 1
                    if created_count % 50 == 0:  # نمایش پیشرفت هر 50 رکورد
                        print(f"✅ {created_count} تراکنش وارد شد...")
                
                except Exception as e:
                    print(f"⚠️  خطا در پردازش ردیف {row_num}: {e}")
                    error_count += 1
                    continue
            
            print(f"\n=== خلاصه وارد کردن ===")
            print(f"✅ تعداد تراکنش‌های وارد شده: {created_count}")
            print(f"⚠️  تعداد ردیف‌های نادیده گرفته شده: {skipped_count}")
            print(f"❌ تعداد خطاها: {error_count}")
            print(f"⚠️  تعداد عدم تطابق تاریخ‌ها: {date_mismatch_count}")
            print(f"📊 مجموع ردیف‌های پردازش شده: {created_count + skipped_count + error_count}")
            
    except FileNotFoundError:
        print(f"❌ فایل پیدا نشد: {csv_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ خطا در وارد کردن داده‌ها: {e}")
        sys.exit(1)


def main():
    """
    تابع اصلی اسکریپت
    """
    print(f"🚀 شروع وارد کردن تراکنش‌ها از: {CSV_FILE_PATH}")
    
    # بررسی وجود فایل
    if not CSV_FILE_PATH.exists():
        print(f"❌ فایل CSV موجود نیست: {CSV_FILE_PATH}")
        sys.exit(1)
    
    # نمایش تعداد رکوردهای موجود قبل از وارد کردن
    existing_count = Transaction.objects.count()
    print(f"📊 تعداد تراکنش‌های موجود در دیتابیس: {existing_count}")
    
    # وارد کردن داده‌ها
    import_transactions_from_csv(CSV_FILE_PATH)
    
    # نمایش تعداد نهایی
    final_count = Transaction.objects.count()
    print(f"📊 تعداد نهایی تراکنش‌ها در دیتابیس: {final_count}")
    print(f"➕ تراکنش‌های جدید اضافه شده: {final_count - existing_count}")


if __name__ == '__main__':
    main()

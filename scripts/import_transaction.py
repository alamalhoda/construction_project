#!/usr/bin/env python
"""
اسکریپت وارد کردن تراکنش‌ها از فایل CSV به دیتابیس Django

این اسکریپت شامل ویژگی‌های زیر است:
1. تبدیل تاریخ شمسی به میلادی و مقایسه با تاریخ موجود در CSV
2. محاسبه خودکار day_remaining و day_from_start و مقایسه با مقادیر CSV
3. اعتبارسنجی کامل داده‌ها قبل از وارد کردن
4. گزارش‌دهی جامع از عملیات انجام شده

نحوه استفاده:
source env/bin/activate && python scripts/import_transaction.py
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

# تعداد رکوردهای مورد نظر برای تست (None = همه رکوردها)
TEST_LIMIT = 10


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


def validate_date_conversion(shamsi_date_str, gregorian_date_str, row_index, silent=False, validation_results=None):
    """
    اعتبارسنجی تبدیل تاریخ شمسی به میلادی
    """
    # تجزیه تاریخ شمسی
    shamsi_date = parse_shamsi_date(shamsi_date_str)
    if not shamsi_date:
        if not silent:
            print(f"⚠️  خطا در تجزیه تاریخ شمسی در ردیف {row_index}: {shamsi_date_str}")
        return None, None, False
    
    # تبدیل شمسی به میلادی
    converted_gregorian = shamsi_date.togregorian()
    
    # تجزیه تاریخ میلادی از فایل
    file_gregorian = parse_gregorian_date(gregorian_date_str)
    if not file_gregorian:
        if not silent:
            print(f"⚠️  خطا در تجزیه تاریخ میلادی در ردیف {row_index}: {gregorian_date_str}")
        return shamsi_date, None, False
    
    # مقایسه تاریخ‌ها
    if converted_gregorian != file_gregorian:
        if not silent:
            print(f"⚠️  عدم تطابق تاریخ‌ها در ردیف {row_index}:")
            print(f"    تاریخ شمسی: {shamsi_date_str} -> تبدیل شده: {converted_gregorian}")
            print(f"    تاریخ میلادی فایل: {file_gregorian}")
        
        # ذخیره جزئیات عدم تطابق
        if validation_results:
            validation_results['date_mismatch_details'].append({
                'row': row_index,
                'shamsi': shamsi_date_str,
                'converted_gregorian': converted_gregorian,
                'file_gregorian': file_gregorian
            })
        
        return shamsi_date, file_gregorian, False
    
    return shamsi_date, file_gregorian, True


def calculate_and_validate_days(project, transaction_date, csv_day_remaining, csv_day_from_start, row_index, silent=False, validation_results=None):
    """
    محاسبه و اعتبارسنجی روزهای مانده و از شروع
    """
    calculated_day_remaining = 0
    calculated_day_from_start = 0
    days_valid = True
    
    # محاسبه روز مانده تا پایان پروژه
    if project.end_date_gregorian and transaction_date:
        calculated_day_remaining = (project.end_date_gregorian - transaction_date).days
    
    # محاسبه روز از ابتدای پروژه  
    if project.start_date_gregorian and transaction_date:
        calculated_day_from_start = (transaction_date - project.start_date_gregorian).days
    
    # مقایسه day_remaining
    if calculated_day_remaining != csv_day_remaining:
        if not silent:
            print(f"⚠️  عدم تطابق روز مانده در ردیف {row_index}:")
            print(f"    محاسبه شده: {calculated_day_remaining}")
            print(f"    مقدار CSV: {csv_day_remaining}")
        days_valid = False
    
    # مقایسه day_from_start
    if calculated_day_from_start != csv_day_from_start:
        if not silent:
            print(f"⚠️  عدم تطابق روز از شروع در ردیف {row_index}:")
            print(f"    محاسبه شده: {calculated_day_from_start}")
            print(f"    مقدار CSV: {csv_day_from_start}")
        days_valid = False
    
    # ذخیره جزئیات عدم تطابق
    if not days_valid and validation_results:
        validation_results['days_mismatch_details'].append({
            'row': row_index,
            'calculated_day_remaining': calculated_day_remaining,
            'csv_day_remaining': csv_day_remaining,
            'calculated_day_from_start': calculated_day_from_start,
            'csv_day_from_start': csv_day_from_start,
            'transaction_date': transaction_date
        })
    
    return calculated_day_remaining, calculated_day_from_start, days_valid


def get_or_create_project(project_name, silent=False):
    """
    دریافت یا ایجاد پروژه
    """
    try:
        project = Project.objects.get(name=project_name)
        return project
    except Project.DoesNotExist:
        if not silent:
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


def get_investor_by_name(full_name, silent=False):
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
        if not silent:
            print(f"⚠️  سرمایه‌گذار '{full_name}' یافت نشد.")
        return None


def get_period_by_label(project, period_label, silent=False):
    """
    یافتن دوره بر اساس عنوان
    """
    try:
        period = Period.objects.get(project=project, label=period_label)
        return period
    except Period.DoesNotExist:
        if not silent:
            print(f"⚠️  دوره '{period_label}' برای پروژه '{project.name}' یافت نشد.")
        return None


def validate_csv_data(csv_file_path):
    """
    اعتبارسنجی داده‌های CSV بدون ذخیره در دیتابیس
    """
    validation_results = {
        'total_rows': 0,
        'valid_rows': 0,
        'invalid_rows': 0,
        'date_mismatches': 0,
        'days_mismatches': 0,
        'missing_investors': [],
        'missing_periods': [],
        'invalid_amounts': [],
        'invalid_dates': [],
        'errors': [],
        'date_mismatch_details': [],
        'days_mismatch_details': []
    }
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            print("🔍 شروع اعتبارسنجی داده‌ها...")
            if TEST_LIMIT:
                print(f"📝 حالت تست: فقط {TEST_LIMIT} رکورد اول بررسی می‌شود")
            print("=" * 60)
            
            for row_num, row in enumerate(csv_reader, start=2):
                # محدودیت تعداد رکوردها برای تست
                if TEST_LIMIT and validation_results['total_rows'] >= TEST_LIMIT:
                    print(f"⏹️  توقف در رکورد {TEST_LIMIT} (حالت تست)")
                    break
                validation_results['total_rows'] += 1
                row_valid = True
                
                try:
                    # استخراج داده‌ها از CSV (با رفع مشکل BOM)
                    project_id = row.get('project_id', '') or row.get('\ufeffproject_id', '')
                    project_id = project_id.strip()
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
                        validation_results['errors'].append(f"ردیف {row_num}: داده‌های ناقص")
                        row_valid = False
                    
                    # اعتبارسنجی تاریخ‌ها
                    if row_valid:
                        shamsi_date, gregorian_date, date_valid = validate_date_conversion(
                            date_shamsi_str, date_gregorian_str, row_num, silent=True, validation_results=validation_results
                        )
                        
                        if not shamsi_date or not gregorian_date:
                            validation_results['invalid_dates'].append(row_num)
                            row_valid = False
                        elif not date_valid:
                            validation_results['date_mismatches'] += 1
                    
                    # بررسی پروژه
                    if row_valid:
                        project = get_or_create_project(project_id, silent=True)
                        
                        # بررسی سرمایه‌گذار
                        investor = get_investor_by_name(investor_name, silent=True)
                        if not investor:
                            validation_results['missing_investors'].append(f"ردیف {row_num}: {investor_name}")
                            row_valid = False
                        
                        # بررسی دوره
                        period = get_period_by_label(project, period_label, silent=True)
                        if not period:
                            validation_results['missing_periods'].append(f"ردیف {row_num}: {period_label}")
                            row_valid = False
                        
                        # اعتبارسنجی مبلغ
                        try:
                            amount = Decimal(amount_str)
                        except (InvalidOperation, ValueError):
                            validation_results['invalid_amounts'].append(f"ردیف {row_num}: {amount_str}")
                            row_valid = False
                        
                        # اعتبارسنجی روزها
                        if row_valid:
                            try:
                                csv_day_remaining = int(day_remaining_str) if day_remaining_str else 0
                                csv_day_from_start = int(day_from_start_str) if day_from_start_str else 0
                                
                                calculated_day_remaining, calculated_day_from_start, days_valid = calculate_and_validate_days(
                                    project, gregorian_date, csv_day_remaining, csv_day_from_start, row_num, silent=True, validation_results=validation_results
                                )
                                
                                if not days_valid:
                                    validation_results['days_mismatches'] += 1
                                    
                            except ValueError:
                                validation_results['errors'].append(f"ردیف {row_num}: خطا در تبدیل روزها")
                                row_valid = False
                    
                    if row_valid:
                        validation_results['valid_rows'] += 1
                    else:
                        validation_results['invalid_rows'] += 1
                        
                except Exception as e:
                    validation_results['errors'].append(f"ردیف {row_num}: {str(e)}")
                    validation_results['invalid_rows'] += 1
            
            return validation_results
            
    except FileNotFoundError:
        print(f"❌ فایل پیدا نشد: {csv_file_path}")
        return None
    except Exception as e:
        print(f"❌ خطا در اعتبارسنجی: {e}")
        return None


def import_transactions_from_csv(csv_file_path, skip_validation=False):
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
            days_mismatch_count = 0
            
            for row_num, row in enumerate(csv_reader, start=2):  # شروع از ردیف 2 (بعد از header)
                try:
                    # استخراج داده‌ها از CSV (با رفع مشکل BOM)
                    project_id = row.get('project_id', '') or row.get('\ufeffproject_id', '')
                    project_id = project_id.strip()
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
                    
                    # تبدیل day_remaining و day_from_start از CSV
                    try:
                        csv_day_remaining = int(day_remaining_str) if day_remaining_str else 0
                        csv_day_from_start = int(day_from_start_str) if day_from_start_str else 0
                    except ValueError:
                        print(f"⚠️  خطا در تبدیل روزها در ردیف {row_num}")
                        csv_day_remaining = 0
                        csv_day_from_start = 0
                    
                    # محاسبه و اعتبارسنجی روزها
                    calculated_day_remaining, calculated_day_from_start, days_valid = calculate_and_validate_days(
                        project, gregorian_date, csv_day_remaining, csv_day_from_start, row_num
                    )
                    
                    if not days_valid:
                        days_mismatch_count += 1
                        # ادامه پردازش با مقادیر محاسبه شده
                    
                    # ایجاد تراکنش با مقادیر محاسبه شده
                    transaction = Transaction.objects.create(
                        project=project,
                        investor=investor,
                        period=period,
                        date_shamsi=shamsi_date,
                        date_gregorian=gregorian_date,
                        amount=amount,
                        transaction_type=entry_type,
                        description=f"وارد شده از فایل CSV - ردیف {row_num}",
                        day_remaining=calculated_day_remaining,
                        day_from_start=calculated_day_from_start,
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
            print(f"⚠️  تعداد عدم تطابق روزها: {days_mismatch_count}")
            print(f"📊 مجموع ردیف‌های پردازش شده: {created_count + skipped_count + error_count}")
            
    except FileNotFoundError:
        print(f"❌ فایل پیدا نشد: {csv_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ خطا در وارد کردن داده‌ها: {e}")
        sys.exit(1)


def print_validation_report(results):
    """
    نمایش گزارش اعتبارسنجی
    """
    print("\n📋 گزارش اعتبارسنجی:")
    print("=" * 60)
    print(f"📊 کل ردیف‌ها: {results['total_rows']}")
    print(f"✅ ردیف‌های معتبر: {results['valid_rows']}")
    print(f"❌ ردیف‌های نامعتبر: {results['invalid_rows']}")
    print(f"⚠️  عدم تطابق تاریخ‌ها: {results['date_mismatches']}")
    print(f"⚠️  عدم تطابق روزها: {results['days_mismatches']}")
    
    if results['missing_investors']:
        print(f"\n👤 سرمایه‌گذاران یافت نشده ({len(results['missing_investors'])}):")
        for investor in results['missing_investors'][:5]:  # نمایش 5 مورد اول
            print(f"  - {investor}")
        if len(results['missing_investors']) > 5:
            print(f"  ... و {len(results['missing_investors']) - 5} مورد دیگر")
    
    if results['missing_periods']:
        print(f"\n📅 دوره‌های یافت نشده ({len(results['missing_periods'])}):")
        for period in results['missing_periods'][:5]:
            print(f"  - {period}")
        if len(results['missing_periods']) > 5:
            print(f"  ... و {len(results['missing_periods']) - 5} مورد دیگر")
    
    if results['invalid_amounts']:
        print(f"\n💰 مبالغ نامعتبر ({len(results['invalid_amounts'])}):")
        for amount in results['invalid_amounts'][:5]:
            print(f"  - {amount}")
        if len(results['invalid_amounts']) > 5:
            print(f"  ... و {len(results['invalid_amounts']) - 5} مورد دیگر")
    
    if results['errors']:
        print(f"\n❌ خطاهای عمومی ({len(results['errors'])}):")
        for error in results['errors'][:5]:
            print(f"  - {error}")
        if len(results['errors']) > 5:
            print(f"  ... و {len(results['errors']) - 5} مورد دیگر")
    
    # نمایش جزئیات عدم تطابق تاریخ‌ها
    if results['date_mismatch_details']:
        print(f"\n📅 جزئیات عدم تطابق تاریخ‌ها ({len(results['date_mismatch_details'])}):")
        for detail in results['date_mismatch_details'][:3]:  # نمایش 3 مورد اول
            print(f"  ردیف {detail['row']}:")
            print(f"    شمسی: {detail['shamsi']} → {detail['converted_gregorian']}")
            print(f"    فایل: {detail['file_gregorian']}")
        if len(results['date_mismatch_details']) > 3:
            print(f"  ... و {len(results['date_mismatch_details']) - 3} مورد دیگر")
    
    # نمایش جزئیات عدم تطابق روزها
    if results['days_mismatch_details']:
        print(f"\n⏰ جزئیات عدم تطابق روزها ({len(results['days_mismatch_details'])}):")
        for detail in results['days_mismatch_details'][:3]:  # نمایش 3 مورد اول
            print(f"  ردیف {detail['row']} (تاریخ: {detail['transaction_date']}):")
            if detail['calculated_day_remaining'] != detail['csv_day_remaining']:
                print(f"    روز مانده: محاسبه={detail['calculated_day_remaining']}, CSV={detail['csv_day_remaining']}")
            if detail['calculated_day_from_start'] != detail['csv_day_from_start']:
                print(f"    روز از شروع: محاسبه={detail['calculated_day_from_start']}, CSV={detail['csv_day_from_start']}")
        if len(results['days_mismatch_details']) > 3:
            print(f"  ... و {len(results['days_mismatch_details']) - 3} مورد دیگر")
    
    print("=" * 60)
    
    # بررسی آمادگی برای وارد کردن
    can_import = (results['invalid_rows'] == 0 and 
                  len(results['missing_investors']) == 0 and 
                  len(results['missing_periods']) == 0 and 
                  len(results['invalid_amounts']) == 0 and 
                  len(results['invalid_dates']) == 0 and
                  len(results['errors']) == 0)
    
    if can_import:
        print("✅ همه داده‌ها معتبر هستند. آماده وارد کردن به دیتابیس.")
        if results['date_mismatches'] > 0 or results['days_mismatches'] > 0:
            print("⚠️  توجه: عدم تطابق‌هایی وجود دارد اما داده‌ها قابل وارد کردن هستند.")
    else:
        print("❌ داده‌های نامعتبر وجود دارد. لطفاً ابتدا خطاها را برطرف کنید.")
    
    return can_import


def main():
    """
    تابع اصلی اسکریپت
    """
    print(f"🚀 شروع پردازش فایل: {CSV_FILE_PATH}")
    
    # بررسی وجود فایل
    if not CSV_FILE_PATH.exists():
        print(f"❌ فایل CSV موجود نیست: {CSV_FILE_PATH}")
        sys.exit(1)
    
    # مرحله 1: اعتبارسنجی داده‌ها
    print("\n🔍 مرحله 1: اعتبارسنجی داده‌ها...")
    validation_results = validate_csv_data(CSV_FILE_PATH)
    
    if validation_results is None:
        print("❌ خطا در اعتبارسنجی فایل")
        sys.exit(1)
    
    # نمایش گزارش اعتبارسنجی
    can_import = print_validation_report(validation_results)
    
    if not can_import:
        print("\n❌ به دلیل وجود خطاهای اعتبارسنجی، عملیات متوقف شد.")
        sys.exit(1)
    
    # مرحله 2: وارد کردن داده‌ها
    print("\n💾 مرحله 2: وارد کردن داده‌ها به دیتابیس...")
    
    # نمایش تعداد رکوردهای موجود قبل از وارد کردن
    existing_count = Transaction.objects.count()
    print(f"📊 تعداد تراکنش‌های موجود در دیتابیس: {existing_count}")
    
    # تأیید نهایی از کاربر
    if validation_results['date_mismatches'] > 0 or validation_results['days_mismatches'] > 0:
        print(f"\n⚠️  هشدار: {validation_results['date_mismatches']} عدم تطابق تاریخ و {validation_results['days_mismatches']} عدم تطابق روز وجود دارد.")
        print("آیا می‌خواهید با وجود این عدم تطابق‌ها ادامه دهید؟")
        print("برای ادامه 'yes' تایپ کنید، برای لغو Enter بزنید:")
        
        try:
            user_input = input().strip().lower()
            if user_input != 'yes':
                print("❌ عملیات لغو شد.")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\n❌ عملیات لغو شد.")
            sys.exit(0)
    
    # وارد کردن داده‌ها
    import_transactions_from_csv(CSV_FILE_PATH, skip_validation=True)
    
    # نمایش تعداد نهایی
    final_count = Transaction.objects.count()
    print(f"📊 تعداد نهایی تراکنش‌ها در دیتابیس: {final_count}")
    print(f"➕ تراکنش‌های جدید اضافه شده: {final_count - existing_count}")
    print("\n🎉 عملیات با موفقیت کامل شد!")


if __name__ == '__main__':
    main()

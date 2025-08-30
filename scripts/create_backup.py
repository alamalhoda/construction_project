#!/usr/bin/env python
"""
اسکریپت پشتیبان‌گیری پیشرفته از دیتابیس

این اسکریپت:
1. پوشه‌ای با تاریخ و ساعت فعلی ایجاد می‌کند
2. یک fixture کامل از همه داده‌ها
3. fixture جداگانه از هر جدول
4. فایل آمار و گزارش

استفاده:
python scripts/create_backup.py
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime
import json

# اضافه کردن مسیر پروژه به Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# تنظیم متغیر محیطی Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')

# راه‌اندازی Django
django.setup()

from django.core.management import call_command
from construction.models import Project, Investor, Period, Transaction, Unit


def create_backup_directory():
    """
    ایجاد پوشه backup با تاریخ و ساعت فعلی
    """
    now = datetime.now()
    
    # فرمت: backup_20240831_021730 (سال-ماه-روز_ساعت-دقیقه-ثانیه)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/backup_{timestamp}"
    
    # ایجاد پوشه اصلی backups اگر وجود ندارد
    Path("backups").mkdir(exist_ok=True)
    
    # ایجاد پوشه backup جدید
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)
    
    return backup_path, timestamp


def get_database_stats():
    """
    دریافت آمار داده‌های موجود در دیتابیس
    """
    stats = {
        'projects': Project.objects.count(),
        'investors': Investor.objects.count(),
        'periods': Period.objects.count(),
        'transactions': Transaction.objects.count(),
        'units': Unit.objects.count()
    }
    
    stats['total'] = sum(stats.values())
    return stats


def create_complete_fixture(backup_path):
    """
    ایجاد fixture کامل از همه داده‌ها
    """
    print("📦 ایجاد fixture کامل...")
    
    complete_file = backup_path / "complete_database.json"
    
    try:
        call_command(
            'dumpdata', 
            'construction',
            indent=2,
            output=str(complete_file)
        )
        print(f"  ✅ {complete_file.name}")
        return True
    except Exception as e:
        print(f"  ❌ خطا در ایجاد fixture کامل: {e}")
        return False


def create_individual_fixtures(backup_path):
    """
    ایجاد fixture جداگانه برای هر جدول
    """
    print("📋 ایجاد fixtures جداگانه...")
    
    models = [
        ('construction.project', 'projects.json', 'پروژه‌ها'),
        ('construction.investor', 'investors.json', 'سرمایه‌گذاران'),
        ('construction.period', 'periods.json', 'دوره‌ها'),
        ('construction.transaction', 'transactions.json', 'تراکنش‌ها'),
        ('construction.unit', 'units.json', 'واحدها')
    ]
    
    success_count = 0
    
    for model, filename, persian_name in models:
        try:
            file_path = backup_path / filename
            call_command(
                'dumpdata',
                model,
                indent=2,
                output=str(file_path)
            )
            print(f"  ✅ {filename} ({persian_name})")
            success_count += 1
        except Exception as e:
            print(f"  ❌ خطا در {persian_name}: {e}")
    
    return success_count


def create_stats_file(backup_path, timestamp, stats):
    """
    ایجاد فایل آمار و گزارش
    """
    print("📊 ایجاد فایل آمار...")
    
    now = datetime.now()
    
    # آمار انواع تراکنش‌ها
    transaction_stats = {}
    if stats['transactions'] > 0:
        try:
            for tx_type, display_name in Transaction.TRANSACTION_TYPES:
                count = Transaction.objects.filter(transaction_type=tx_type).count()
                positive_count = Transaction.objects.filter(
                    transaction_type=tx_type, 
                    amount__gt=0
                ).count()
                negative_count = Transaction.objects.filter(
                    transaction_type=tx_type, 
                    amount__lt=0
                ).count()
                
                transaction_stats[tx_type] = {
                    'display_name': display_name,
                    'total': count,
                    'positive': positive_count,
                    'negative': negative_count
                }
        except Exception as e:
            transaction_stats = {'error': str(e)}
    
    report_data = {
        'backup_info': {
            'timestamp': timestamp,
            'persian_date': now.strftime("%Y/%m/%d"),
            'persian_time': now.strftime("%H:%M:%S"),
            'backup_directory': str(backup_path.name)
        },
        'database_stats': stats,
        'transaction_details': transaction_stats,
        'files_created': [
            'complete_database.json',
            'projects.json',
            'investors.json', 
            'periods.json',
            'transactions.json',
            'units.json',
            'backup_report.json',
            'backup_summary.txt'
        ]
    }
    
    # فایل JSON برای خواندن ماشینی
    json_report = backup_path / "backup_report.json"
    with open(json_report, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    # فایل متنی برای خواندن انسانی
    text_report = backup_path / "backup_summary.txt"
    with open(text_report, 'w', encoding='utf-8') as f:
        f.write("📦 گزارش پشتیبان‌گیری دیتابیس\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"📅 تاریخ: {now.strftime('%Y/%m/%d')}\n")
        f.write(f"🕐 ساعت: {now.strftime('%H:%M:%S')}\n")
        f.write(f"📁 پوشه: {backup_path.name}\n\n")
        
        f.write("📊 آمار داده‌ها:\n")
        f.write(f"  پروژه‌ها: {stats['projects']}\n")
        f.write(f"  سرمایه‌گذاران: {stats['investors']}\n")
        f.write(f"  دوره‌ها: {stats['periods']}\n")
        f.write(f"  تراکنش‌ها: {stats['transactions']}\n")
        f.write(f"  واحدها: {stats['units']}\n")
        f.write(f"  کل رکوردها: {stats['total']}\n\n")
        
        if transaction_stats and 'error' not in transaction_stats:
            f.write("💰 تفصیل تراکنش‌ها:\n")
            for tx_type, data in transaction_stats.items():
                f.write(f"  {data['display_name']}:\n")
                f.write(f"    کل: {data['total']}\n")
                f.write(f"    مثبت: {data['positive']}\n")
                f.write(f"    منفی: {data['negative']}\n")
        
        f.write("\n📁 فایل‌های ایجاد شده:\n")
        for filename in report_data['files_created']:
            f.write(f"  ✅ {filename}\n")
        
        f.write(f"\n🔄 نحوه بازیابی:\n")
        f.write(f"  python scripts/restore_backup.py\n")
        f.write(f"  یا\n")
        f.write(f"  python manage.py loaddata {backup_path.name}/complete_database.json\n")
    
    print(f"  ✅ backup_report.json")
    print(f"  ✅ backup_summary.txt")


def main():
    """
    تابع اصلی
    """
    print("🚀 شروع پشتیبان‌گیری پیشرفته")
    print("=" * 60)
    
    # ایجاد پوشه backup
    backup_path, timestamp = create_backup_directory()
    print(f"📁 پوشه backup: {backup_path}")
    
    # دریافت آمار دیتابیس
    stats = get_database_stats()
    print(f"📊 کل داده‌ها: {stats['total']} رکورد")
    
    # ایجاد fixtures
    complete_success = create_complete_fixture(backup_path)
    individual_count = create_individual_fixtures(backup_path)
    
    # ایجاد فایل آمار
    create_stats_file(backup_path, timestamp, stats)
    
    # گزارش نهایی
    print("\n" + "=" * 60)
    
    if complete_success and individual_count == 5:
        print("🎉 پشتیبان‌گیری با موفقیت کامل شد!")
        print(f"📁 مسیر: {backup_path}")
        print(f"📦 فایل‌های ایجاد شده: {len(os.listdir(backup_path))}")
        
        # محاسبه حجم کل
        total_size = sum(
            os.path.getsize(backup_path / f) 
            for f in os.listdir(backup_path)
        )
        size_kb = total_size / 1024
        print(f"💾 حجم کل: {size_kb:.1f} KB")
        
    else:
        print("⚠️  پشتیبان‌گیری با مشکل مواجه شد!")
        print(f"Fixture کامل: {'✅' if complete_success else '❌'}")
        print(f"Fixtures جداگانه: {individual_count}/5")
    
    print("\n🔄 برای بازیابی:")
    print(f"python scripts/restore_backup.py")
    print("یا")
    print(f"python manage.py loaddata {backup_path.name}/complete_database.json")


if __name__ == '__main__':
    main()

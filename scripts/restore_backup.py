#!/usr/bin/env python
"""
اسکریپت بازیابی دیتابیس از fixture

استفاده:
python scripts/restore_backup.py

⚠️ هشدار: این اسکریپت همه داده‌های فعلی را پاک می‌کند!
"""

import os
import sys
import django
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# تنظیم متغیر محیطی Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construction_project.settings')

# راه‌اندازی Django
django.setup()

from django.core.management import call_command
from construction.models import Project, Investor, Period, Transaction, Unit


def main():
    """
    تابع اصلی - بازیابی دیتابیس از backup
    """
    print("🔄 اسکریپت بازیابی دیتابیس")
    print("=" * 60)
    
    # نمایش وضعیت فعلی
    print("📊 وضعیت فعلی دیتابیس:")
    current_projects = Project.objects.count()
    current_investors = Investor.objects.count()
    current_periods = Period.objects.count()
    current_transactions = Transaction.objects.count()
    current_units = Unit.objects.count()
    
    print(f"  پروژه‌ها: {current_projects}")
    print(f"  سرمایه‌گذاران: {current_investors}")
    print(f"  دوره‌ها: {current_periods}")
    print(f"  تراکنش‌ها: {current_transactions}")
    print(f"  واحدها: {current_units}")
    
    total_current = current_projects + current_investors + current_periods + current_transactions + current_units
    print(f"  کل: {total_current} رکورد")
    
    # اخطار
    print("\n⚠️  هشدار:")
    print("این عملیات همه داده‌های فعلی را پاک کرده و با backup جایگزین می‌کند!")
    
    # تأیید کاربر
    try:
        user_input = input("\nآیا مطمئن هستید؟ برای ادامه 'YES' تایپ کنید: ").strip()
        if user_input != 'YES':
            print("❌ عملیات لغو شد.")
            return
    except KeyboardInterrupt:
        print("\n❌ عملیات لغو شد.")
        return
    
    print("\n🗑️  پاک کردن داده‌های فعلی...")
    
    # پاک کردن داده‌های فعلی (به ترتیب وابستگی)
    Transaction.objects.all().delete()
    print("  ✅ تراکنش‌ها پاک شدند")
    
    Period.objects.all().delete()
    print("  ✅ دوره‌ها پاک شدند")
    
    # پاک کردن جدول ManyToMany
    for investor in Investor.objects.all():
        investor.units.clear()
    
    Investor.objects.all().delete()
    print("  ✅ سرمایه‌گذاران پاک شدند")
    
    Unit.objects.all().delete()
    print("  ✅ واحدها پاک شدند")
    
    Project.objects.all().delete()
    print("  ✅ پروژه‌ها پاک شدند")
    
    print("\n📥 بارگذاری داده‌ها از backup...")
    
    # جستجو برای جدیدترین backup
    backup_dirs = []
    if os.path.exists('backups'):
        backup_dirs = [d for d in os.listdir('backups') if d.startswith('backup_')]
        backup_dirs.sort(reverse=True)  # جدیدترین اول
    
    # انتخاب فایل fixture
    fixture_path = None
    
    if backup_dirs:
        latest_backup = backup_dirs[0]
        fixture_path = f'backups/{latest_backup}/complete_database.json'
        print(f"📁 استفاده از جدیدترین backup: {latest_backup}")
    else:
        # fallback به backup قدیمی
        fixture_path = 'construction/fixtures/complete_data_backup.json'
        print(f"📁 استفاده از backup اصلی")
    
    if not os.path.exists(fixture_path):
        print(f"❌ فایل backup یافت نشد: {fixture_path}")
        
        # نمایش backups موجود
        if backup_dirs:
            print("\n📋 Backups موجود:")
            for backup_dir in backup_dirs[:5]:  # 5 تای جدید
                print(f"  - {backup_dir}")
            print("\nمی‌توانید دستی استفاده کنید:")
            print(f"python manage.py loaddata backups/[backup_name]/complete_database.json")
        
        return
    
    try:
        call_command('loaddata', fixture_path)
        print("  ✅ داده‌ها با موفقیت بارگذاری شدند")
    except Exception as e:
        print(f"❌ خطا در بارگذاری: {e}")
        return
    
    # نمایش وضعیت جدید
    print("\n📊 وضعیت جدید دیتابیس:")
    new_projects = Project.objects.count()
    new_investors = Investor.objects.count()
    new_periods = Period.objects.count()
    new_transactions = Transaction.objects.count()
    new_units = Unit.objects.count()
    
    print(f"  پروژه‌ها: {new_projects}")
    print(f"  سرمایه‌گذاران: {new_investors}")
    print(f"  دوره‌ها: {new_periods}")
    print(f"  تراکنش‌ها: {new_transactions}")
    print(f"  واحدها: {new_units}")
    
    total_new = new_projects + new_investors + new_periods + new_transactions + new_units
    print(f"  کل: {total_new} رکورد")
    
    print("\n🎉 بازیابی با موفقیت انجام شد!")
    print("=" * 60)


if __name__ == '__main__':
    main()

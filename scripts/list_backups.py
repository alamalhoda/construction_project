#!/usr/bin/env python
"""
اسکریپت لیست کردن backups موجود

استفاده:
python scripts/list_backups.py
"""

import os
import json
from pathlib import Path
from datetime import datetime


def format_timestamp(timestamp):
    """
    تبدیل timestamp به فرمت خوانا
    """
    try:
        # فرمت: 20250830_225642
        date_part = timestamp[:8]  # 20250830
        time_part = timestamp[9:]  # 225642
        
        year = date_part[:4]
        month = date_part[4:6]
        day = date_part[6:8]
        
        hour = time_part[:2]
        minute = time_part[2:4]
        second = time_part[4:6]
        
        return f"{year}/{month}/{day} - {hour}:{minute}:{second}"
    except:
        return timestamp


def get_backup_size(backup_path):
    """
    محاسبه حجم backup
    """
    try:
        total_size = sum(
            os.path.getsize(backup_path / f) 
            for f in os.listdir(backup_path)
        )
        return total_size / 1024  # KB
    except:
        return 0


def read_backup_info(backup_path):
    """
    خواندن اطلاعات backup از فایل گزارش
    """
    report_file = backup_path / "backup_report.json"
    if report_file.exists():
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return None


def main():
    """
    تابع اصلی
    """
    print("📋 لیست Backups موجود")
    print("=" * 60)
    
    backups_dir = Path("backups")
    
    if not backups_dir.exists():
        print("❌ پوشه backups وجود ندارد!")
        print("💡 برای ایجاد backup جدید:")
        print("python scripts/create_backup.py")
        return
    
    # جستجو برای backups
    backup_dirs = [
        d for d in backups_dir.iterdir() 
        if d.is_dir() and d.name.startswith('backup_')
    ]
    
    if not backup_dirs:
        print("❌ هیچ backup یافت نشد!")
        print("💡 برای ایجاد backup جدید:")
        print("python scripts/create_backup.py")
        return
    
    # مرتب‌سازی بر اساس تاریخ (جدیدترین اول)
    backup_dirs.sort(key=lambda x: x.name, reverse=True)
    
    print(f"📊 تعداد backups: {len(backup_dirs)}\n")
    
    for i, backup_dir in enumerate(backup_dirs, 1):
        print(f"🗂️  #{i} - {backup_dir.name}")
        
        # اطلاعات زمانی
        timestamp = backup_dir.name.replace('backup_', '')
        formatted_time = format_timestamp(timestamp)
        print(f"   📅 تاریخ: {formatted_time}")
        
        # حجم
        size_kb = get_backup_size(backup_dir)
        print(f"   💾 حجم: {size_kb:.1f} KB")
        
        # اطلاعات تفصیلی از فایل گزارش
        backup_info = read_backup_info(backup_dir)
        if backup_info:
            stats = backup_info.get('database_stats', {})
            if stats:
                total_records = stats.get('total', 0)
                print(f"   📊 رکوردها: {total_records}")
                print(f"      - پروژه‌ها: {stats.get('projects', 0)}")
                print(f"      - سرمایه‌گذاران: {stats.get('investors', 0)}")
                print(f"      - دوره‌ها: {stats.get('periods', 0)}")
                print(f"      - تراکنش‌ها: {stats.get('transactions', 0)}")
                print(f"      - واحدها: {stats.get('units', 0)}")
        
        # فایل‌های موجود
        files = list(backup_dir.iterdir())
        print(f"   📁 فایل‌ها: {len(files)}")
        
        # فایل‌های مهم
        important_files = [
            'complete_database.json',
            'transactions.json', 
            'backup_summary.txt'
        ]
        
        missing_files = []
        for file in important_files:
            if not (backup_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"   ⚠️  فایل‌های ناقص: {', '.join(missing_files)}")
        else:
            print(f"   ✅ کامل")
        
        print()
    
    # راهنمای استفاده
    print("🔄 نحوه بازیابی:")
    print("1. استفاده از اسکریپت (جدیدترین backup):")
    print("   python scripts/restore_backup.py")
    print()
    print("2. بازیابی دستی backup خاص:")
    if backup_dirs:
        latest = backup_dirs[0].name
        print(f"   python manage.py loaddata backups/{latest}/complete_database.json")
    print()
    print("3. بازیابی فقط یک جدول:")
    if backup_dirs:
        latest = backup_dirs[0].name
        print(f"   python manage.py loaddata backups/{latest}/transactions.json")


if __name__ == '__main__':
    main()

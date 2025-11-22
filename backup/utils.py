"""
ابزارهای کمکی برای مدیریت بک‌آپ
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import shutil

from django.core.management import call_command
from django.apps import apps


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


def get_database_stats(project_id=None):
    """
    دریافت آمار داده‌های موجود در دیتابیس
    
    Args:
        project_id: شناسه پروژه برای فیلتر کردن داده‌ها (اختیاری)
    """
    try:
        Project = apps.get_model('construction', 'Project')
        Investor = apps.get_model('construction', 'Investor')
        Period = apps.get_model('construction', 'Period')
        Transaction = apps.get_model('construction', 'Transaction')
        Unit = apps.get_model('construction', 'Unit')
        
        InterestRate = apps.get_model('construction', 'InterestRate')
        Expense = apps.get_model('construction', 'Expense')
        Sale = apps.get_model('construction', 'Sale')
        UserProfile = apps.get_model('construction', 'UserProfile')
        
        User = apps.get_model('auth', 'User')
        Group = apps.get_model('auth', 'Group')
        BackupRecord = apps.get_model('backup', 'BackupRecord')
        BackupSettings = apps.get_model('backup', 'BackupSettings')
        
        # فیلتر بر اساس پروژه - برای مدل Project باید از id استفاده کنیم
        project_filter = {}
        if project_id:
            project_filter['id'] = project_id
        
        # فیلتر برای مدل‌هایی که project دارند - باید از project_id استفاده کنیم
        project_related_filter = {}
        if project_id:
            project_related_filter['project_id'] = project_id
        
        stats = {
            # مدل‌های construction - فیلتر بر اساس پروژه
            'projects': Project.objects.filter(**project_filter).count() if project_id else Project.objects.count(),
            'investors': Investor.objects.filter(**project_related_filter).count() if project_id else Investor.objects.count(),
            'periods': Period.objects.filter(**project_related_filter).count() if project_id else Period.objects.count(),
            'transactions': Transaction.objects.filter(**project_related_filter).count() if project_id else Transaction.objects.count(),
            'units': Unit.objects.filter(**project_related_filter).count() if project_id else Unit.objects.count(),
            'interest_rates': InterestRate.objects.filter(**project_related_filter).count() if project_id else InterestRate.objects.count(),
            'expenses': Expense.objects.filter(**project_related_filter).count() if project_id else Expense.objects.count(),
            'sales': Sale.objects.filter(**project_related_filter).count() if project_id else Sale.objects.count(),
            'user_profiles': UserProfile.objects.count(),  # user profiles معمولاً به پروژه مربوط نیستند
            
            # مدل‌های Django داخلی - همیشه همه
            'users': User.objects.count(),
            'groups': Group.objects.count(),
            
            # مدل‌های backup - همیشه همه
            'backup_records': BackupRecord.objects.count(),
            'backup_settings': BackupSettings.objects.count(),
        }
        
        stats['total'] = sum(stats.values())
        return stats
    except Exception as e:
        print(f"خطا در دریافت آمار دیتابیس: {e}")
        return {
            # مدل‌های construction
            'projects': 0,
            'investors': 0,
            'periods': 0,
            'transactions': 0,
            'units': 0,
            'interest_rates': 0,
            'expenses': 0,
            'sales': 0,
            'user_profiles': 0,
            
            # مدل‌های Django داخلی
            'users': 0,
            'groups': 0,
            
            # مدل‌های backup
            'backup_records': 0,
            'backup_settings': 0,
            'total': 0
        }


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
            'auth',
            'contenttypes',
            'sessions',
            'admin',
            'backup',
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
        # مدل‌های construction
        ('construction.project', 'projects.json', 'پروژه‌ها'),
        ('construction.investor', 'investors.json', 'سرمایه‌گذاران'),
        ('construction.period', 'periods.json', 'دوره‌ها'),
        ('construction.transaction', 'transactions.json', 'تراکنش‌ها'),
        ('construction.unit', 'units.json', 'واحدها'),
        ('construction.interestrate', 'interest_rates.json', 'نرخ‌های سود'),
        ('construction.expense', 'expenses.json', 'هزینه‌ها'),
        ('construction.sale', 'sales.json', 'فروش‌ها'),
        ('construction.userprofile', 'user_profiles.json', 'پروفایل‌های کاربری'),
        
        # مدل‌های Django داخلی
        ('auth.user', 'users.json', 'کاربران'),
        ('auth.group', 'groups.json', 'گروه‌ها'),
        ('auth.permission', 'permissions.json', 'مجوزها'),
        ('contenttypes.contenttype', 'content_types.json', 'انواع محتوا'),
        ('sessions.session', 'sessions.json', 'جلسات'),
        ('admin.logentry', 'admin_logs.json', 'لاگ‌های ادمین'),
        
        # مدل‌های backup
        ('backup.backuprecord', 'backup_records.json', 'رکوردهای بک‌آپ'),
        ('backup.backupsettings', 'backup_settings.json', 'تنظیمات بک‌آپ'),
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
            Transaction = apps.get_model('construction', 'Transaction')
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
            'interest_rates.json',
            'expenses.json',
            'sales.json',
            'user_profiles.json',
            'users.json',
            'groups.json',
            'permissions.json',
            'content_types.json',
            'sessions.json',
            'admin_logs.json',
            'backup_records.json',
            'backup_settings.json',
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
        f.write("  مدل‌های construction:\n")
        f.write(f"    پروژه‌ها: {stats['projects']}\n")
        f.write(f"    سرمایه‌گذاران: {stats['investors']}\n")
        f.write(f"    دوره‌ها: {stats['periods']}\n")
        f.write(f"    تراکنش‌ها: {stats['transactions']}\n")
        f.write(f"    واحدها: {stats['units']}\n")
        f.write(f"    نرخ‌های سود: {stats['interest_rates']}\n")
        f.write(f"    هزینه‌ها: {stats['expenses']}\n")
        f.write(f"    فروش‌ها: {stats['sales']}\n")
        f.write(f"    پروفایل‌های کاربری: {stats['user_profiles']}\n")
        f.write("  مدل‌های Django:\n")
        f.write(f"    کاربران: {stats['users']}\n")
        f.write(f"    گروه‌ها: {stats['groups']}\n")
        f.write("  مدل‌های backup:\n")
        f.write(f"    رکوردهای بک‌آپ: {stats['backup_records']}\n")
        f.write(f"    تنظیمات بک‌آپ: {stats['backup_settings']}\n")
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


def format_timestamp(timestamp):
    """
    تبدیل timestamp به فرمت خوانا
    """
    try:
        date_part = timestamp[:8]
        time_part = timestamp[9:]
        
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


def cleanup_old_backups(max_backups=10, cleanup_after_days=30):
    """
    پاک‌سازی بک‌آپ‌های قدیمی
    """
    deleted_count = 0
    
    try:
        BackupRecord = apps.get_model('backup', 'BackupRecord')
        
        # حذف بک‌آپ‌های قدیمی از دیتابیس
        cutoff_date = datetime.now() - timedelta(days=cleanup_after_days)
        old_backups = BackupRecord.objects.filter(
            created_at__lt=cutoff_date,
            status='completed'
        ).order_by('created_at')
        
        # نگه داشتن فقط جدیدترین بک‌آپ‌ها
        if old_backups.count() > max_backups:
            backups_to_delete = old_backups[:old_backups.count() - max_backups]
            
            for backup in backups_to_delete:
                # حذف فایل‌های فیزیکی
                if backup.file_path and os.path.exists(backup.file_path):
                    shutil.rmtree(backup.file_path)
                
                # حذف رکورد از دیتابیس
                backup.delete()
                deleted_count += 1
        
        # پاک‌سازی فایل‌های فیزیکی بدون رکورد دیتابیس
        backups_dir = Path("backups")
        if backups_dir.exists():
            for backup_dir in backups_dir.iterdir():
                if backup_dir.is_dir() and backup_dir.name.startswith('backup_'):
                    # بررسی وجود رکورد در دیتابیس
                    backup_name = backup_dir.name
                    if not BackupRecord.objects.filter(name=backup_name).exists():
                        # حذف پوشه قدیمی
                        shutil.rmtree(backup_dir)
                        deleted_count += 1
        
        return deleted_count
        
    except Exception as e:
        print(f"خطا در پاک‌سازی بک‌آپ‌ها: {e}")
        return deleted_count


def create_backup_with_record():
    """
    ایجاد بک‌آپ با ثبت در دیتابیس
    """
    try:
        BackupRecord = apps.get_model('backup', 'BackupRecord')
        
        # ایجاد رکورد بک‌آپ
        backup_record = BackupRecord.objects.create(
            name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            backup_type='manual',
            status='running'
        )
        
        # ایجاد پوشه backup
        backup_path, timestamp = create_backup_directory()
        
        # دریافت آمار دیتابیس
        stats = get_database_stats()
        
        # ایجاد fixtures
        complete_success = create_complete_fixture(backup_path)
        individual_count = create_individual_fixtures(backup_path)
        
        # ایجاد فایل آمار
        create_stats_file(backup_path, timestamp, stats)
        
        # به‌روزرسانی رکورد
        if complete_success and individual_count == 17:
            backup_record.status = 'completed'
            backup_record.completed_at = datetime.now()
            backup_record.success_message = "بک‌آپ با موفقیت ایجاد شد"
        else:
            backup_record.status = 'failed'
            backup_record.completed_at = datetime.now()
            backup_record.error_message = f"خطا در ایجاد fixture: {individual_count}/17"
        
        # آمار داده‌ها
        backup_record.projects_count = stats['projects']
        backup_record.investors_count = stats['investors']
        backup_record.periods_count = stats['periods']
        backup_record.transactions_count = stats['transactions']
        backup_record.units_count = stats['units']
        backup_record.interest_rates_count = stats['interest_rates']
        backup_record.expenses_count = stats['expenses']
        backup_record.sales_count = stats['sales']
        backup_record.user_profiles_count = stats['user_profiles']
        backup_record.total_records = stats['total']
        
        # اطلاعات فایل
        backup_record.file_path = str(backup_path)
        backup_record.file_size_kb = get_backup_size(backup_path)
        
        backup_record.save()
        
        return backup_record
        
    except Exception as e:
        # در صورت خطا، رکورد را به‌روزرسانی کن
        if 'backup_record' in locals():
            backup_record.status = 'failed'
            backup_record.completed_at = datetime.now()
            backup_record.error_message = str(e)
            backup_record.save()
        
        raise e

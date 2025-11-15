#!/usr/bin/env python
"""
اسکریپت پشتیبان‌گیری پیشرفته از دیتابیس

این اسکریپت:
1. پوشه‌ای با تاریخ و ساعت فعلی ایجاد می‌کند
2. یک fixture کامل از داده‌های پروژه انتخاب شده
3. fixture جداگانه از هر جدول مربوط به پروژه
4. فایل آمار و گزارش

استفاده:
python scripts/create_backup.py [project_id]

اگر project_id داده نشود، از همه داده‌ها بک‌آپ می‌گیرد.
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
from django.core import serializers
from construction.models import Project, Investor, Period, Transaction, Unit, InterestRate, Expense, Sale, UserProfile

# دریافت project_id از آرگومان خط فرمان
project_id = None
if len(sys.argv) > 1:
    try:
        project_id = int(sys.argv[1])
    except ValueError:
        print(f"❌ خطا: شناسه پروژه نامعتبر است: {sys.argv[1]}")
        sys.exit(1)

# Import SecurityEvent if available
try:
    from construction.security_monitoring import SecurityEvent
    SECURITY_EVENT_AVAILABLE = True
except ImportError:
    SecurityEvent = None
    SECURITY_EVENT_AVAILABLE = False


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
    from django.contrib.auth.models import User, Group
    from backup.models import BackupRecord
    
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
        
        # مدل‌های امنیتی (حذف شده - جدول وجود ندارد)
        # 'security_events': SecurityEvent.objects.count() if SECURITY_EVENT_AVAILABLE else 0,
    }
    
    stats['total'] = sum(stats.values())
    return stats


def create_complete_fixture(backup_path, project_id=None):
    """
    ایجاد fixture کامل از داده‌ها
    
    Args:
        backup_path: مسیر پوشه بک‌آپ
        project_id: شناسه پروژه برای فیلتر کردن (اختیاری)
    """
    print("📦 ایجاد fixture کامل...")
    
    complete_file = backup_path / "complete_database.json"
    
    try:
        # اگر project_id مشخص شده باشد، فقط از داده‌های آن پروژه بک‌آپ بگیر
        if project_id:
            # ابتدا پروژه را بخوان
            try:
                project = Project.objects.get(pk=project_id)
                print(f"  📁 پروژه: {project.name}")
            except Project.DoesNotExist:
                print(f"  ❌ پروژه با شناسه {project_id} یافت نشد")
                return False
            
            # ایجاد fixture کامل با استفاده از serialization مستقیم
            # این روش دقیق‌تر است و فقط داده‌های پروژه را شامل می‌شود
            
            from django.apps import apps as django_apps
            from django.contrib.auth.models import User, Group, Permission
            from django.contrib.contenttypes.models import ContentType
            from django.contrib.sessions.models import Session
            from django.contrib.admin.models import LogEntry
            from backup.models import BackupRecord, BackupSettings
            
            all_fixtures = []
            
            # 1. پروژه انتخاب شده
            project_queryset = Project.objects.filter(pk=project_id)
            project_serialized = serializers.serialize('json', project_queryset, use_natural_foreign_keys=True, use_natural_primary_keys=True)
            if project_serialized:
                all_fixtures.append(project_serialized)
            
            # 2. مدل‌های مرتبط با پروژه
            related_models_config = [
                ('construction', 'Investor'),
                ('construction', 'Period'),
                ('construction', 'Transaction'),
                ('construction', 'Unit'),
                ('construction', 'InterestRate'),
                ('construction', 'Expense'),
                ('construction', 'Sale'),
            ]
            
            for app_name, model_name in related_models_config:
                try:
                    model_class = django_apps.get_model(app_name, model_name)
                    queryset = model_class.objects.filter(project_id=project_id)
                    if queryset.exists():
                        serialized = serializers.serialize('json', queryset, use_natural_foreign_keys=True, use_natural_primary_keys=True)
                        all_fixtures.append(serialized)
                except Exception as e:
                    print(f"  ⚠️  خطا در serialization {app_name}.{model_name}: {e}")
            
            # 3. مدل‌های construction که به پروژه مربوط نیستند (یا همه)
            try:
                user_profiles = UserProfile.objects.all()
                if user_profiles.exists():
                    serialized = serializers.serialize('json', user_profiles, use_natural_foreign_keys=True, use_natural_primary_keys=True)
                    all_fixtures.append(serialized)
            except Exception as e:
                print(f"  ⚠️  خطا در serialization UserProfile: {e}")
            
            # 4. مدل‌های Django (auth, contenttypes, sessions, admin, backup)
            django_models = [
                (User,),
                (Group,),
                (Permission,),
                (ContentType,),
                (Session,),
                (LogEntry,),
                (BackupRecord,),
                (BackupSettings,),
            ]
            
            for model_class in django_models:
                try:
                    queryset = model_class[0].objects.all()
                    if queryset.exists():
                        serialized = serializers.serialize('json', queryset, use_natural_foreign_keys=True, use_natural_primary_keys=True)
                        all_fixtures.append(serialized)
                except Exception as e:
                    print(f"  ⚠️  خطا در serialization {model_class[0].__name__}: {e}")
            
            # ادغام همه fixture ها
            import json
            all_data = []
            for fixture_json in all_fixtures:
                if fixture_json:
                    try:
                        data = json.loads(fixture_json)
                        if isinstance(data, list):
                            all_data.extend(data)
                        else:
                            all_data.append(data)
                    except Exception as e:
                        print(f"  ⚠️  خطا در parsing fixture: {e}")
            
            # ذخیره فایل
            with open(complete_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            print(f"  📊 تعداد کل رکوردها: {len(all_data)}")
        else:
            # بک‌آپ کامل از همه داده‌ها
            call_command(
                'dumpdata', 
                'construction',
                'auth',
                'contenttypes',
                'sessions',
                'admin',
                'backup',
                '--exclude', 'construction.securityevent',  # حذف SecurityEvent
                indent=2,
                output=str(complete_file)
            )
        
        print(f"  ✅ {complete_file.name}")
        return True
    except Exception as e:
        print(f"  ❌ خطا در ایجاد fixture کامل: {e}")
        return False


def filter_fixture_by_project(fixture_file, project_id):
    """
    فیلتر کردن fixture بر اساس project_id
    
    Args:
        fixture_file: مسیر فایل fixture
        project_id: شناسه پروژه
    """
    try:
        with open(fixture_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # دریافت اطلاعات پروژه
        try:
            project = Project.objects.get(pk=project_id)
            project_pk = project_id
            project_name = project.name
        except Project.DoesNotExist:
            print(f"  ❌ پروژه با شناسه {project_id} یافت نشد")
            return
        
        # فیلتر کردن داده‌ها
        filtered_data = []
        project_found = False
        
        # پیدا کردن پروژه
        for item in data:
            if item.get('model') == 'construction.project':
                item_pk = item.get('pk')
                # بررسی ID
                if item_pk == project_pk:
                    project_found = True
                    filtered_data.append(item)
                    break
                # بررسی natural key (اگر استفاده شده باشد)
                elif isinstance(item_pk, list) and len(item_pk) > 0:
                    if str(item_pk[0]) == str(project_name) or str(item_pk[0]) == str(project_pk):
                        project_found = True
                        filtered_data.append(item)
                        break
        
        if not project_found:
            print(f"  ⚠️  هشدار: پروژه با شناسه {project_id} در fixture یافت نشد")
            # اگر پروژه یافت نشد، حداقل سعی کنیم داده‌ها را فیلتر کنیم
        
        # فیلتر کردن داده‌های مرتبط
        related_models = [
            'construction.investor',
            'construction.period',
            'construction.transaction',
            'construction.unit',
            'construction.interestrate',
            'construction.expense',
            'construction.sale',
        ]
        
        # مجموعه‌ای برای جلوگیری از تکرار مدل‌های غیر مرتبط
        non_related_items = {}
        
        for item in data:
            model = item.get('model', '')
            
            # اگر پروژه است، قبلاً اضافه شده
            if model == 'construction.project':
                # همه پروژه‌های دیگر را نادیده بگیر
                continue
            
            # اگر مدل مرتبط با پروژه است
            if model in related_models:
                fields = item.get('fields', {})
                item_project = fields.get('project')
                
                # بررسی اینکه آیا این آیتم به پروژه مربوط است
                is_related = False
                
                # حالت 1: project به صورت عددی (ID)
                if item_project == project_pk:
                    is_related = True
                
                # حالت 2: project به صورت natural key (لیست)
                elif isinstance(item_project, list):
                    if len(item_project) > 0:
                        # natural key می‌تواند نام پروژه یا ID باشد
                        item_key = str(item_project[0])
                        if item_key == str(project_name) or item_key == str(project_pk):
                            is_related = True
                
                # حالت 3: project به صورت رشته (natural key بدون لیست)
                elif isinstance(item_project, str):
                    if item_project == project_name or item_project == str(project_pk):
                        is_related = True
                
                if is_related:
                    filtered_data.append(item)
            else:
                # مدل‌های دیگر را بدون فیلتر اضافه کن (auth, contenttypes, etc.)
                # اما فقط یک بار اضافه می‌کنیم (بر اساس مدل و pk)
                model_key = (model, item.get('pk'))
                if model_key not in non_related_items:
                    non_related_items[model_key] = item
                    filtered_data.append(item)
        
        # ذخیره فایل فیلتر شده
        with open(fixture_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ فیلتر شده: {len(filtered_data)} رکورد (از {len(data)} رکورد اصلی)")
        
    except Exception as e:
        print(f"  ❌ خطا در فیلتر کردن fixture: {e}")
        import traceback
        traceback.print_exc()


def create_individual_fixtures(backup_path, project_id=None):
    """
    ایجاد fixture جداگانه برای هر جدول
    
    Args:
        backup_path: مسیر پوشه بک‌آپ
        project_id: شناسه پروژه برای فیلتر کردن (اختیاری)
    """
    print("📋 ایجاد fixtures جداگانه...")
    
    # مدل‌های مرتبط با پروژه
    project_related_models = [
        ('construction.investor', 'investors.json', 'سرمایه‌گذاران'),
        ('construction.period', 'periods.json', 'دوره‌ها'),
        ('construction.transaction', 'transactions.json', 'تراکنش‌ها'),
        ('construction.unit', 'units.json', 'واحدها'),
        ('construction.interestrate', 'interest_rates.json', 'نرخ‌های سود'),
        ('construction.expense', 'expenses.json', 'هزینه‌ها'),
        ('construction.sale', 'sales.json', 'فروش/مرجوعی‌ها'),
    ]
    
    # مدل‌های دیگر
    other_models = [
        # مدل‌های construction
        ('construction.project', 'projects.json', 'پروژه‌ها'),
        ('construction.userprofile', 'user_profiles.json', 'پروفایل‌های کاربران'),
        
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
        
        # مدل‌های امنیتی (فقط در صورت وجود)
        # ('construction.securityevent', 'security_events.json', 'رویدادهای امنیتی'),
    ]
    
    success_count = 0
    
    # فیلتر کردن مدل‌های مرتبط با پروژه
    if project_id:
        try:
            project = Project.objects.get(pk=project_id)
            print(f"  📁 فیلتر بر اساس پروژه: {project.name}")
        except Project.DoesNotExist:
            print(f"  ❌ پروژه با شناسه {project_id} یافت نشد")
            return 0
        
        # فقط پروژه انتخاب شده
        try:
            file_path = backup_path / 'projects.json'
            call_command(
                'dumpdata',
                'construction.project',
                f'--pks={project_id}',
                indent=2,
                output=str(file_path)
            )
            print(f"  ✅ projects.json (پروژه‌ها)")
            success_count += 1
        except Exception as e:
            print(f"  ❌ خطا در پروژه‌ها: {e}")
        
        # مدل‌های مرتبط با پروژه - با فیلتر مستقیم از queryset
        for model_name, filename, persian_name in project_related_models:
            try:
                file_path = backup_path / filename
                
                # استخراج نام مدل و app
                app_name, model_class_name = model_name.split('.')
                
                # دریافت مدل
                from django.apps import apps
                model_class = apps.get_model(app_name, model_class_name)
                
                # فیلتر کردن queryset بر اساس پروژه
                queryset = model_class.objects.filter(project_id=project_id)
                
                # استفاده از serialization مستقیم
                with open(file_path, 'w', encoding='utf-8') as f:
                    serializers.serialize('json', queryset, 
                                         use_natural_foreign_keys=True,
                                         use_natural_primary_keys=True,
                                         indent=2,
                                         stream=f,
                                         ensure_ascii=False)
                
                count = queryset.count()
                print(f"  ✅ {filename} ({persian_name}) - {count} رکورد")
                success_count += 1
            except Exception as e:
                print(f"  ❌ خطا در {persian_name}: {e}")
                import traceback
                traceback.print_exc()
    else:
        # همه مدل‌های مرتبط با پروژه بدون فیلتر
        for model, filename, persian_name in project_related_models:
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
    
    # مدل‌های دیگر (بدون فیلتر)
    for model, filename, persian_name in other_models:
        try:
            file_path = backup_path / filename
            if project_id and model == 'construction.project':
                # پروژه قبلاً اضافه شده
                continue
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


def create_stats_file(backup_path, timestamp, stats, project_id=None):
    """
    ایجاد فایل آمار و گزارش
    
    Args:
        backup_path: مسیر پوشه بک‌آپ
        timestamp: زمان‌بندی بک‌آپ
        stats: آمار دیتابیس
        project_id: شناسه پروژه (اختیاری)
    """
    print("📊 ایجاد فایل آمار...")
    
    now = datetime.now()
    
    # فیلتر بر اساس پروژه
    project_filter = {}
    if project_id:
        project_filter['project_id'] = project_id
        try:
            project = Project.objects.get(pk=project_id)
            project_name = project.name
        except Project.DoesNotExist:
            project_name = f"پروژه {project_id}"
    else:
        project_name = "همه پروژه‌ها"
    
    # آمار انواع تراکنش‌ها
    transaction_stats = {}
    if stats['transactions'] > 0:
        try:
            for tx_type, display_name in Transaction.TRANSACTION_TYPES:
                base_query = Transaction.objects.filter(transaction_type=tx_type)
                if project_id:
                    base_query = base_query.filter(**project_filter)
                
                count = base_query.count()
                positive_count = base_query.filter(amount__gt=0).count()
                negative_count = base_query.filter(amount__lt=0).count()
                
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
            'backup_directory': str(backup_path.name),
            'project_id': project_id,
            'project_name': project_name if project_id else None
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
            # 'security_events.json',
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
        f.write(f"📁 پوشه: {backup_path.name}\n")
        if project_id:
            f.write(f"📁 پروژه: {project_name} (شناسه: {project_id})\n")
        f.write("\n")
        
        f.write("📊 آمار داده‌ها:\n")
        f.write("  مدل‌های construction:\n")
        f.write(f"    پروژه‌ها: {stats['projects']}\n")
        f.write(f"    سرمایه‌گذاران: {stats['investors']}\n")
        f.write(f"    دوره‌ها: {stats['periods']}\n")
        f.write(f"    تراکنش‌ها: {stats['transactions']}\n")
        f.write(f"    واحدها: {stats['units']}\n")
        f.write(f"    نرخ‌های سود: {stats['interest_rates']}\n")
        f.write(f"    هزینه‌ها: {stats['expenses']}\n")
        f.write(f"    فروش/مرجوعی‌ها: {stats['sales']}\n")
        f.write(f"    پروفایل‌های کاربران: {stats['user_profiles']}\n")
        f.write("  مدل‌های Django:\n")
        f.write(f"    کاربران: {stats['users']}\n")
        f.write(f"    گروه‌ها: {stats['groups']}\n")
        f.write("  مدل‌های backup:\n")
        f.write(f"    رکوردهای بک‌آپ: {stats['backup_records']}\n")
        # f.write("  مدل‌های امنیتی:\n")
        # f.write(f"    رویدادهای امنیتی: {stats['security_events']}\n")
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
    global project_id
    
    print("🚀 شروع پشتیبان‌گیری پیشرفته")
    print("=" * 60)
    
    if project_id:
        try:
            project = Project.objects.get(pk=project_id)
            print(f"📁 پروژه انتخابی: {project.name}")
        except Project.DoesNotExist:
            print(f"❌ خطا: پروژه با شناسه {project_id} یافت نشد")
            sys.exit(1)
    else:
        print("⚠️  توجه: بک‌آپ از همه داده‌ها تهیه می‌شود")
    
    # ایجاد پوشه backup
    backup_path, timestamp = create_backup_directory()
    print(f"📁 پوشه backup: {backup_path}")
    
    # دریافت آمار دیتابیس
    stats = get_database_stats(project_id)
    print(f"📊 کل داده‌ها: {stats['total']} رکورد")
    if project_id:
        print(f"📊 داده‌های پروژه: {stats['transactions']} تراکنش، {stats['investors']} سرمایه‌گذار")
    
    # ایجاد fixtures
    complete_success = create_complete_fixture(backup_path, project_id)
    individual_count = create_individual_fixtures(backup_path, project_id)
    
    # ایجاد فایل آمار
    create_stats_file(backup_path, timestamp, stats, project_id)
    
    # گزارش نهایی
    print("\n" + "=" * 60)
    
    if complete_success and individual_count == 17:  # 18 - 1 (security_events)
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
        print(f"Fixtures جداگانه: {individual_count}/17")
    
    print("\n🔄 برای بازیابی:")
    print(f"python scripts/restore_backup.py")
    print("یا")
    print(f"python manage.py loaddata {backup_path.name}/complete_database.json")


if __name__ == '__main__':
    main()

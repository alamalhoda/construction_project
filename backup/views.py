from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# مسیر ریشه پروژه
project_root = Path(settings.BASE_DIR)

from .models import BackupRecord, BackupSettings
from .utils import (
    create_backup_directory,
    get_database_stats,
    create_complete_fixture,
    create_individual_fixtures,
    create_stats_file,
    format_timestamp,
    get_backup_size,
    read_backup_info,
    cleanup_old_backups
)


def backup_dashboard(request):
    """صفحه اصلی داشبورد بک‌آپ"""
    # آمار کلی
    total_backups = BackupRecord.objects.count()
    successful_backups = BackupRecord.objects.filter(status='completed').count()
    failed_backups = BackupRecord.objects.filter(status='failed').count()
    
    # آخرین بک‌آپ‌ها
    recent_backups = BackupRecord.objects.all()[:5]
    
    # آمار دیتابیس فعلی
    current_stats = get_database_stats()
    
    # تنظیمات
    backup_settings = BackupSettings.get_settings()
    
    context = {
        'total_backups': total_backups,
        'successful_backups': successful_backups,
        'failed_backups': failed_backups,
        'recent_backups': recent_backups,
        'current_stats': current_stats,
        'backup_settings': backup_settings,
    }
    
    return render(request, 'backup/backup_dashboard.html', context)


def backup_list(request):
    """لیست تمام بک‌آپ‌ها"""
    backups = BackupRecord.objects.all()
    
    # فیلتر بر اساس وضعیت
    status_filter = request.GET.get('status')
    if status_filter:
        backups = backups.filter(status=status_filter)
    
    # فیلتر بر اساس نوع
    type_filter = request.GET.get('type')
    if type_filter:
        backups = backups.filter(backup_type=type_filter)
    
    # صفحه‌بندی
    paginator = Paginator(backups, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': BackupRecord._meta.get_field('status').choices,
        'type_choices': BackupRecord._meta.get_field('backup_type').choices,
        'current_status': status_filter,
        'current_type': type_filter,
    }
    
    return render(request, 'backup/list.html', context)


def backup_detail(request, pk):
    """جزئیات یک بک‌آپ"""
    backup = get_object_or_404(BackupRecord, pk=pk)
    
    # خواندن اطلاعات تفصیلی از فایل
    backup_info = None
    if backup.file_path and os.path.exists(backup.file_path):
        backup_dir = Path(backup.file_path).parent
        backup_info = read_backup_info(backup_dir)
    
    context = {
        'backup': backup,
        'backup_info': backup_info,
    }
    
    return render(request, 'backup/detail.html', context)


def backup_settings_view(request):
    """صفحه تنظیمات بک‌آپ"""
    settings_obj = BackupSettings.get_settings()
    
    if request.method == 'POST':
        # به‌روزرسانی تنظیمات
        settings_obj.auto_backup_enabled = request.POST.get('auto_backup_enabled') == 'on'
        settings_obj.auto_backup_interval = int(request.POST.get('auto_backup_interval', 24))
        settings_obj.auto_backup_time = request.POST.get('auto_backup_time', '02:00')
        settings_obj.max_backups = int(request.POST.get('max_backups', 10))
        settings_obj.auto_cleanup_enabled = request.POST.get('auto_cleanup_enabled') == 'on'
        settings_obj.cleanup_after_days = int(request.POST.get('cleanup_after_days', 30))
        settings_obj.compression_enabled = request.POST.get('compression_enabled') == 'on'
        settings_obj.include_media_files = request.POST.get('include_media_files') == 'on'
        settings_obj.email_notifications = request.POST.get('email_notifications') == 'on'
        settings_obj.notification_email = request.POST.get('notification_email', '')
        
        settings_obj.save()
        messages.success(request, 'تنظیمات با موفقیت ذخیره شد.')
        return redirect('backup:settings')
    
    context = {
        'settings': settings_obj,
    }
    
    return render(request, 'backup/settings.html', context)


def download_backup(request, pk):
    """دانلود فایل بک‌آپ"""
    backup = get_object_or_404(BackupRecord, pk=pk)
    
    if backup.status != 'completed':
        return JsonResponse({
            'success': False,
            'message': 'بک‌آپ هنوز تکمیل نشده است'
        })
    
    if not backup.file_path or not os.path.exists(backup.file_path):
        return JsonResponse({
            'success': False,
            'message': 'فایل بک‌آپ یافت نشد'
        })
    
    # ایجاد فایل ZIP از پوشه بک‌آپ
    import zipfile
    import tempfile
    
    backup_path = Path(backup.file_path)
    zip_filename = f"{backup.name}.zip"
    
    # ایجاد فایل ZIP موقت
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    
    with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in backup_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(backup_path)
                zipf.write(file_path, arcname)
    
    # ارسال فایل ZIP
    response = HttpResponse(
        open(temp_zip.name, 'rb').read(),
        content_type='application/zip'
    )
    response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
    
    # حذف فایل موقت
    os.unlink(temp_zip.name)
    
    return response


@require_POST
@csrf_exempt
def cleanup_backups_api(request):
    """API برای پاک‌سازی بک‌آپ‌های قدیمی"""
    try:
        settings = BackupSettings.get_settings()
        deleted_count = cleanup_old_backups(
            max_backups=settings.max_backups,
            cleanup_after_days=settings.cleanup_after_days
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} بک‌آپ قدیمی حذف شد',
            'deleted_count': deleted_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا در پاک‌سازی: {str(e)}'
        })


@require_POST
@csrf_exempt
def manage_cron_api(request):
    """API برای مدیریت cron job"""
    try:
        action = request.POST.get('action')
        
        if action == 'enable':
            # فعال کردن cron
            import subprocess
            result = subprocess.run(['./scripts/setup_cron.sh'], 
                                  capture_output=True, text=True, cwd=project_root)
            
            if result.returncode == 0:
                return JsonResponse({
                    'success': True,
                    'message': 'Cron job با موفقیت فعال شد'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'خطا در فعال کردن cron: {result.stderr}'
                })
                
        elif action == 'disable':
            # غیرفعال کردن cron
            import subprocess
            result = subprocess.run(['./scripts/remove_cron.sh'], 
                                  capture_output=True, text=True, cwd=project_root)
            
            if result.returncode == 0:
                return JsonResponse({
                    'success': True,
                    'message': 'Cron job با موفقیت غیرفعال شد'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'خطا در غیرفعال کردن cron: {result.stderr}'
                })
                
        elif action == 'status':
            # بررسی وضعیت cron
            import subprocess
            result = subprocess.run(['crontab', '-l'], 
                                  capture_output=True, text=True)
            
            backup_script = str(project_root / 'scripts/run_auto_backup.sh')
            is_enabled = backup_script in result.stdout
            
            return JsonResponse({
                'success': True,
                'enabled': is_enabled,
                'cron_output': result.stdout if result.returncode == 0 else ''
            })
            
        else:
            return JsonResponse({
                'success': False,
                'message': 'عملیات نامعتبر'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا در مدیریت cron: {str(e)}'
        })


@require_POST
@csrf_exempt
def create_backup_api(request):
    """API برای ایجاد بک‌آپ دستی"""
    try:
        # دریافت project_id از درخواست
        project_id = request.POST.get('project_id')
        if not project_id:
            return JsonResponse({
                'success': False,
                'message': 'لطفاً یک پروژه انتخاب کنید'
            })
        
        try:
            project_id = int(project_id)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'شناسه پروژه نامعتبر است'
            })
        
        # بررسی وجود پروژه
        from construction.models import Project
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'پروژه انتخاب شده یافت نشد'
            })
        
        # ایجاد رکورد بک‌آپ
        backup_record = BackupRecord.objects.create(
            name=f"backup_{project.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            backup_type='manual',
            status='running'
        )
        
        # اجرای بک‌آپ با project_id
        result = subprocess.run([
            sys.executable, 
            str(Path(__file__).parent.parent / 'scripts' / 'create_backup.py'),
            str(project_id)
        ], capture_output=True, text=True, cwd=str(Path(__file__).parent.parent))
        
        if result.returncode == 0:
            # به‌روزرسانی رکورد با اطلاعات موفقیت
            backup_record.status = 'completed'
            backup_record.completed_at = timezone.now()
            backup_record.success_message = result.stdout
            
            # آمار دیتابیس (فیلتر شده بر اساس پروژه)
            stats = get_database_stats(project_id)
            backup_record.projects_count = stats['projects']
            backup_record.investors_count = stats['investors']
            backup_record.periods_count = stats['periods']
            backup_record.transactions_count = stats['transactions']
            backup_record.units_count = stats['units']
            backup_record.interest_rates_count = stats['interest_rates']
            backup_record.expenses_count = stats['expenses']
            backup_record.sales_count = stats['sales']
            backup_record.unit_specific_expenses_count = stats['unit_specific_expenses']
            backup_record.petty_cash_transactions_count = stats['petty_cash_transactions']
            backup_record.user_profiles_count = stats['user_profiles']
            backup_record.total_records = stats['total']
            
            # اطلاعات فایل
            backups_dir = Path("backups")
            if backups_dir.exists():
                backup_dirs = [d for d in backups_dir.iterdir() if d.is_dir() and d.name.startswith('backup_')]
                if backup_dirs:
                    latest_backup = max(backup_dirs, key=lambda x: x.name)
                    backup_record.file_path = str(latest_backup)
                    backup_record.file_size_kb = get_backup_size(latest_backup)
            
            backup_record.save()
            
            return JsonResponse({
                'success': True,
                'message': 'بک‌آپ با موفقیت ایجاد شد',
                'backup_id': backup_record.id,
                'output': result.stdout
            })
        else:
            # به‌روزرسانی رکورد با اطلاعات خطا
            backup_record.status = 'failed'
            backup_record.completed_at = timezone.now()
            backup_record.error_message = result.stderr
            backup_record.save()
            
            return JsonResponse({
                'success': False,
                'message': 'خطا در ایجاد بک‌آپ',
                'error': result.stderr
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا در ایجاد بک‌آپ: {str(e)}'
        })


@require_POST
@csrf_exempt
def delete_backup_api(request):
    """API برای حذف بک‌آپ"""
    try:
        backup_id = request.POST.get('backup_id')
        if not backup_id:
            return JsonResponse({
                'success': False,
                'message': 'شناسه بک‌آپ مشخص نشده'
            })
        
        backup_record = get_object_or_404(BackupRecord, pk=backup_id)
        
        # حذف فایل‌های فیزیکی
        if backup_record.file_path and os.path.exists(backup_record.file_path):
            shutil.rmtree(backup_record.file_path)
        
        # حذف رکورد از دیتابیس
        backup_name = backup_record.name
        backup_record.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'بک‌آپ {backup_name} حذف شد'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا در حذف بک‌آپ: {str(e)}'
        })


def get_backup_stats_api(request):
    """API برای دریافت آمار بک‌آپ‌ها"""
    try:
        # آمار دیتابیس
        stats = get_database_stats()
        
        # آمار بک‌آپ‌ها
        total_backups = BackupRecord.objects.count()
        successful_backups = BackupRecord.objects.filter(status='completed').count()
        failed_backups = BackupRecord.objects.filter(status='failed').count()
        
        # حجم کل بک‌آپ‌ها
        total_size = sum(backup.file_size_kb for backup in BackupRecord.objects.filter(status='completed'))
        
        return JsonResponse({
            'success': True,
            'database_stats': stats,
            'backup_stats': {
                'total': total_backups,
                'successful': successful_backups,
                'failed': failed_backups,
                'total_size_kb': total_size
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا در دریافت آمار: {str(e)}'
        })


@require_POST
@csrf_exempt
def cleanup_backups_api(request):
    """API برای پاک‌سازی بک‌آپ‌های قدیمی"""
    try:
        settings_obj = BackupSettings.get_settings()
        
        if not settings_obj.auto_cleanup_enabled:
            return JsonResponse({
                'success': False,
                'message': 'پاک‌سازی خودکار غیرفعال است'
            })
        
        # پاک‌سازی بک‌آپ‌های قدیمی
        deleted_count = cleanup_old_backups(settings_obj.max_backups, settings_obj.cleanup_after_days)
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} بک‌آپ قدیمی حذف شد',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا در پاک‌سازی: {str(e)}'
        })


def download_backup(request, pk):
    """دانلود فایل بک‌آپ"""
    backup = get_object_or_404(BackupRecord, pk=pk)
    
    if not backup.file_path or not os.path.exists(backup.file_path):
        messages.error(request, 'فایل بک‌آپ یافت نشد.')
        return redirect('backup:list')
    
    # ایجاد فایل ZIP از پوشه بک‌آپ
    import zipfile
    import tempfile
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    
    with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        backup_path = Path(backup.file_path)
        for file_path in backup_path.rglob('*'):
            if file_path.is_file():
                zipf.write(file_path, file_path.relative_to(backup_path.parent))
    
    # ارسال فایل
    response = HttpResponse(open(temp_file.name, 'rb').read(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{backup.name}.zip"'
    
    # حذف فایل موقت
    os.unlink(temp_file.name)
    
    return response
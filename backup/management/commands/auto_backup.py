"""
Django management command برای اجرای بک‌آپ خودکار
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from backup.models import BackupSettings, BackupRecord
from backup.utils import create_backup_with_record


class Command(BaseCommand):
    help = 'اجرای بک‌آپ خودکار بر اساس تنظیمات سیستم'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='اجرای اجباری بک‌آپ بدون توجه به تنظیمات زمان',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔄 شروع بررسی بک‌آپ خودکار...')
        )

        try:
            # دریافت تنظیمات
            settings = BackupSettings.get_settings()
            
            if not settings.auto_backup_enabled:
                self.stdout.write(
                    self.style.WARNING('⚠️ بک‌آپ خودکار غیرفعال است')
                )
                return

            # بررسی زمان آخرین بک‌آپ
            if not options['force']:
                if not self.should_run_backup(settings):
                    self.stdout.write(
                        self.style.SUCCESS('✅ زمان بک‌آپ خودکار نرسیده است')
                    )
                    return

            # اجرای بک‌آپ
            self.stdout.write('📦 شروع ایجاد بک‌آپ خودکار...')
            
            backup_record = create_backup_with_record()
            backup_record.backup_type = 'automatic'
            backup_record.save()

            if backup_record.status == 'completed':
                # به‌روزرسانی زمان آخرین بک‌آپ خودکار
                settings.last_auto_backup = timezone.now()
                settings.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ بک‌آپ خودکار با موفقیت ایجاد شد: {backup_record.name}'
                    )
                )
                
                # اجرای پاک‌سازی خودکار
                if settings.auto_cleanup_enabled:
                    from backup.utils import cleanup_old_backups
                    deleted_count = cleanup_old_backups(
                        max_backups=settings.max_backups,
                        cleanup_after_days=settings.cleanup_after_days
                    )
                    
                    if deleted_count > 0:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'🗑️ {deleted_count} بک‌آپ قدیمی حذف شد'
                            )
                        )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ خطا در ایجاد بک‌آپ خودکار: {backup_record.error_message}'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطا در اجرای بک‌آپ خودکار: {str(e)}')
            )

    def should_run_backup(self, settings):
        """
        بررسی اینکه آیا باید بک‌آپ خودکار اجرا شود یا نه
        """
        now = timezone.now()
        
        # اگر هیچ بک‌آپ خودکاری انجام نشده، اجرا کن
        if not settings.last_auto_backup:
            self.stdout.write('📅 اولین بک‌آپ خودکار')
            return True
        
        # محاسبه زمان بعدی بک‌آپ
        next_backup_time = settings.last_auto_backup + timedelta(hours=settings.auto_backup_interval)
        
        # اگر زمان رسیده، اجرا کن
        if now >= next_backup_time:
            self.stdout.write(
                f'⏰ زمان بک‌آپ خودکار رسیده (آخرین: {settings.last_auto_backup.strftime("%Y-%m-%d %H:%M")})'
            )
            return True
        
        # بررسی زمان مشخص شده در روز
        if settings.auto_backup_time:
            try:
                backup_hour, backup_minute = map(int, settings.auto_backup_time.split(':'))
                current_hour = now.hour
                current_minute = now.minute
                
                # اگر زمان مشخص شده رسیده و از آخرین بک‌آپ گذشته
                if (current_hour == backup_hour and 
                    current_minute >= backup_minute and 
                    now.date() > settings.last_auto_backup.date()):
                    self.stdout.write(f'🕐 زمان مشخص شده بک‌آپ رسیده: {settings.auto_backup_time}')
                    return True
            except (ValueError, AttributeError):
                pass
        
        return False

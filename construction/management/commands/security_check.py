"""
دستور بررسی امنیتی
Security Check Management Command
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from construction.security_monitoring import SecurityMonitor, SecurityReport
from construction.data_protection import DataIntegrity, DataRetention
import os

class Command(BaseCommand):
    help = 'بررسی امنیتی پروژه'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-type',
            type=str,
            choices=['all', 'settings', 'data', 'monitoring', 'cleanup'],
            default='all',
            help='نوع بررسی امنیتی'
        )
        parser.add_argument(
            '--fix-issues',
            action='store_true',
            help='رفع مشکلات امنیتی'
        )

    def handle(self, *args, **options):
        check_type = options['check_type']
        fix_issues = options['fix_issues']

        self.stdout.write(
            self.style.SUCCESS('🔒 شروع بررسی امنیتی پروژه')
        )

        if check_type in ['all', 'settings']:
            self.check_security_settings()

        if check_type in ['all', 'data']:
            self.check_data_integrity(fix_issues)

        if check_type in ['all', 'monitoring']:
            self.check_security_monitoring()

        if check_type in ['all', 'cleanup']:
            self.cleanup_old_data()

        self.stdout.write(
            self.style.SUCCESS('✅ بررسی امنیتی تکمیل شد')
        )

    def check_security_settings(self):
        """بررسی تنظیمات امنیتی"""
        self.stdout.write('\n🔧 بررسی تنظیمات امنیتی:')
        
        issues = []
        
        # بررسی DEBUG
        if settings.DEBUG:
            issues.append('❌ DEBUG = True (خطرناک در production)')
        else:
            self.stdout.write('✅ DEBUG = False')
        
        # بررسی ALLOWED_HOSTS
        if not settings.ALLOWED_HOSTS:
            issues.append('❌ ALLOWED_HOSTS خالی است')
        else:
            self.stdout.write('✅ ALLOWED_HOSTS تنظیم شده')
        
        # بررسی SECRET_KEY
        if len(settings.SECRET_KEY) < 50:
            issues.append('⚠️ SECRET_KEY کوتاه است')
        else:
            self.stdout.write('✅ SECRET_KEY طول مناسب دارد')
        
        # نمایش مشکلات
        for issue in issues:
            self.stdout.write(self.style.ERROR(issue))

    def check_data_integrity(self, fix_issues):
        """بررسی یکپارچگی داده‌ها"""
        self.stdout.write('\n📊 بررسی یکپارچگی داده‌ها:')
        
        integrity_issues = DataIntegrity.verify_data_integrity()
        
        if not integrity_issues:
            self.stdout.write('✅ هیچ مشکل یکپارچگی یافت نشد')
        else:
            for issue in integrity_issues:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️ {issue['description']}: {issue['count']} مورد"
                    )
                )
            
            if fix_issues:
                fixed_count = DataIntegrity.fix_integrity_issues(integrity_issues)
                self.stdout.write(
                    self.style.SUCCESS(f"✅ {fixed_count} مشکل رفع شد")
                )

    def check_security_monitoring(self):
        """بررسی نظارت امنیتی"""
        self.stdout.write('\n👁️ بررسی نظارت امنیتی:')
        
        # دریافت آمار داشبورد
        dashboard_data = SecurityMonitor.get_security_dashboard_data()
        
        self.stdout.write(f"📈 رویدادهای 24 ساعت گذشته: {dashboard_data['total_events_24h']}")
        self.stdout.write(f"🚨 رویدادهای بحرانی: {dashboard_data['critical_events']}")
        self.stdout.write(f"🔐 تلاش‌های ورود ناموفق: {dashboard_data['failed_logins']}")
        self.stdout.write(f"⚠️ IP های مشکوک: {dashboard_data['suspicious_ips']}")
        
        # تحلیل فعالیت‌های مشکوک
        SecurityMonitor.analyze_suspicious_activity()
        self.stdout.write('✅ تحلیل فعالیت‌های مشکوک انجام شد')

    def cleanup_old_data(self):
        """پاک کردن داده‌های قدیمی"""
        self.stdout.write('\n🧹 پاک کردن داده‌های قدیمی:')
        
        # پاک کردن داده‌های قدیمی
        cleanup_result = DataRetention.cleanup_old_data()
        
        self.stdout.write(
            f"🗑️ {cleanup_result['deleted_sessions']} session قدیمی حذف شد"
        )
        self.stdout.write(
            f"🗑️ {cleanup_result['deleted_logs']} لاگ قدیمی حذف شد"
        )
        
        # آرشیو داده‌های قدیمی
        archive_result = DataRetention.archive_old_data()
        
        if archive_result['archived_count'] > 0:
            self.stdout.write(
                f"📦 {archive_result['archived_count']} تراکنش قدیمی آرشیو شد"
            )
            self.stdout.write(f"📁 فایل آرشیو: {archive_result['archive_file']}")
        else:
            self.stdout.write('📦 هیچ داده قدیمی برای آرشیو یافت نشد')

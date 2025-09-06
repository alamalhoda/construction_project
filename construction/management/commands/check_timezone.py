"""
Management Command برای بررسی timezone
Check Timezone Management Command
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import datetime
import pytz

class Command(BaseCommand):
    help = 'بررسی تنظیمات timezone و نمایش زمان فعلی'
    
    def handle(self, *args, **options):
        self.stdout.write("🕐 بررسی تنظیمات Timezone")
        self.stdout.write("=" * 50)
        
        # تنظیمات Django
        self.stdout.write(f"📅 TIME_ZONE: {settings.TIME_ZONE}")
        self.stdout.write(f"📅 USE_TZ: {settings.USE_TZ}")
        self.stdout.write(f"📅 USE_I18N: {settings.USE_I18N}")
        self.stdout.write(f"📅 USE_L10N: {settings.USE_L10N}")
        
        # زمان فعلی
        now_utc = datetime.datetime.now(pytz.UTC)
        now_tehran = now_utc.astimezone(pytz.timezone('Asia/Tehran'))
        now_django = timezone.now()
        
        self.stdout.write("\n⏰ زمان‌های فعلی:")
        self.stdout.write(f"🌍 UTC: {now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        self.stdout.write(f"🇮🇷 تهران: {now_tehran.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        self.stdout.write(f"🐍 Django: {now_django.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        # بررسی timezone سیستم
        import os
        system_tz = os.environ.get('TZ', 'Not set')
        self.stdout.write(f"\n💻 متغیر محیطی TZ: {system_tz}")
        
        # تست فرمت فارسی
        try:
            from django.utils.translation import activate
            activate('fa')
            self.stdout.write(f"\n📝 زمان فارسی: {now_django.strftime('%Y/%m/%d %H:%M:%S')}")
        except Exception as e:
            self.stdout.write(f"\n⚠️ خطا در نمایش زمان فارسی: {e}")
        
        self.stdout.write("\n✅ بررسی timezone کامل شد")
